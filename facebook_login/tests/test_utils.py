import pytest
import responses

from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from mixer.backend.django import mixer

from . import utils as test_utils
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

    # TODO: test a bad response


@responses.activate
def test_debug_token():
    test_utils.add_response(DEBUG_TOKEN_URL, {'data': {'user_id': '123'}})
    res = utils.debug_token('valid-token', 'valid-token')
    assert res['data']['user_id'] == '123', (
        "Should return a dict of the form `{'data': {'user_id': '123'}}`")

    # TODO: test a bad response


@responses.activate
def test_get_user_email():
    test_utils.add_response(ME_URL, {'email': 'test@example.com'})
    res = utils.get_user_email('valid-token')
    assert res == 'test@example.com', ('Should return the Facebook user email')

    # TODO: test a bad response
