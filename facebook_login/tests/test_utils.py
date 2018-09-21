import pytest
import responses

from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from mixer.backend.django import mixer

from . import utils as test_utils
from .. import exceptions
from .. import settings
from .. import utils

pytestmark = pytest.mark.django_db

BASE_URL = settings.API_BASE_URL
ACCESS_TOKEN_URL = f'{BASE_URL}/oauth/access_token'
DEBUG_TOKEN_URL = f'{BASE_URL}/debug_token'
ME_URL = f'{BASE_URL}/me'


def test_success_handler_default():
    req = RequestFactory().get('/')
    req.user = AnonymousUser()
    SessionMiddleware().process_request(req)
    req.session.save()

    # before our test, the request user is anonymous
    assert req.user.is_authenticated is False

    user = mixer.blend('auth.User')
    user.backend = 'facebook_login.auth_backends.FacebookAuthBackend'
    res = utils.success_handler_default(req, user)
    # after our test, the request has the authenticated user attached
    assert req.user == user
    assert req.user.is_authenticated is True


@responses.activate
def test_get_app_access_token():
    test_utils.add_response(ACCESS_TOKEN_URL, {'access_token': 'asd'})
    res = utils.get_app_access_token()
    assert res == 'asd', (
        "Should return a dict of the form `{'access_token': 'asd'}`")


@responses.activate
def test_get_app_access_token_error():
    test_utils.add_response(ACCESS_TOKEN_URL, {'access_token': ''})
    with pytest.raises(exceptions.AccessTokenException):
        # Should raise exception if no access_token could be retrieved
        utils.get_app_access_token()


@responses.activate
def test_get_app_access_token_error2():
    # no responses setup, so responses will return a ConnectionError
    with pytest.raises(exceptions.AccessTokenException):
        # Should raise exception if no access_token could be retrieved
        utils.get_app_access_token()


@responses.activate
def test_debug_token():
    test_utils.add_response(DEBUG_TOKEN_URL, {'data': {'user_id': '123'}})
    res = utils.debug_token('valid-token', 'valid-token')
    assert res['data']['user_id'] == '123', (
        "Should return a dict of the form `{'data': {'user_id': '123'}}`")


@responses.activate
def test_debug_token_error1():
    test_utils.add_response(
        DEBUG_TOKEN_URL, {'error': {
            'message': 'Error message from Facebook'
        }})
    try:
        res = utils.debug_token('valid-token', 'valid-token')
    except exceptions.FacebookRequestException as ex:
        assert str(ex) == 'Error message from Facebook', (
            'If Facebook returned an error message, it should be set in this'
            ' exception')


@responses.activate
def test_debug_token_error2():
    # no responses setup, so responses will return a ConnectionError
    with pytest.raises(exceptions.FacebookNetworkException):
        res = utils.debug_token('valid-token', 'valid-token')


@responses.activate
def test_debug_token_error3():
    test_utils.add_response(
        DEBUG_TOKEN_URL,
        {'data': {
            'error': {
                'message': 'Error message from Facebook'
            }
        }})
    with pytest.raises(exceptions.DebugTokenException):
        res = utils.debug_token('valid-token', 'valid-token')


@responses.activate
def test_get_user_email():
    test_utils.add_response(ME_URL, {'email': 'test@example.com'})
    res = utils.get_user_email('valid-token')
    assert res == 'test@example.com', ('Should return the Facebook user email')


@responses.activate
def test_get_user_email_error1():
    test_utils.add_response(ME_URL, {'id': '123'})
    with pytest.raises(exceptions.UserEmailException):
        res = utils.get_user_email('valid-token')


@responses.activate
def test_get_user_email_error2():
    # no responses setup, so responses will return a ConnectionError
    with pytest.raises(exceptions.FacebookNetworkException):
        res = utils.get_user_email('valid-token')


@responses.activate
def test_get_user_email_error3():
    test_utils.add_response(ME_URL, {'error': 'Error message'})
    with pytest.raises(exceptions.FacebookRequestException):
        res = utils.get_user_email('bad-token')
