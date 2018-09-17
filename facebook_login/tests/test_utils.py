import pytest
import responses

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from mixer.backend.django import mixer

from .. import settings
from .. import utils

pytestmark = pytest.mark.django_db


def test_success_handler_default():
    req = RequestFactory().get('/')
    req.user = AnonymousUser()
    SessionMiddleware().process_request(req)
    req.session.save()
    # before our test, the request user is anonymous
    assert req.user.is_authenticated is False

    user = mixer.blend('auth.User')
    res = utils.success_handler_default(req, user)
    # after our test, the request has the authenticated user attached
    assert req.user == user
    assert req.user.is_authenticated is True


@responses.activate
def test_get_app_access_token():
    url = (f'{settings.API_BASE_URL}/oauth/access_token?'
           f'client_id={settings.APP_ID}&'
           f'client_secret={settings.APP_SECRET}&'
           f'grant_type=client_credentials')

    responses.add(
        responses.GET,
        url,
        json={'access_token': 'test-access-token'},
        status=200)

    res = utils.get_app_access_token()
    assert res == 'test-access-token'

    # TODO: test a bad response


@responses.activate
def test_debug_token():
    user_access_token = 'test-user-access-token'
    app_access_token = 'test-app-access-token'

    url = (f'{settings.API_BASE_URL}/debug_token?'
           f'input_token={user_access_token}&'
           f'access_token={app_access_token}')

    responses.add(
        responses.GET,
        url,
        json={'data': {
            'user_id': 'test-fb-user-id'
        }},
        status=200)

    res = utils.debug_token(user_access_token, app_access_token)
    assert res['data']['user_id'] == 'test-fb-user-id'

    # TODO: test a bad response
