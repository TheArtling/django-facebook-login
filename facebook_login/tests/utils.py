import responses
import json

from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from .. import settings

BASE_URL = settings.API_BASE_URL
URLS = {
    'access': f'{BASE_URL}/oauth/access_token',
    'debug': f'{BASE_URL}/debug_token',
    'me': f'{BASE_URL}/me'
}


class InfoFactory(object):
    context = None

    def __init__(self, user=None, *args, **kwargs):
        if user is None:
            user = AnonymousUser()
        self.context = RequestFactory().get('/')
        self.context.user = user
        SessionMiddleware().process_request(self.context)
        self.context.session.save()


def add_response(url, json_response, status=200):
    """Helper function to add a response to responses."""
    responses.add(
        responses.GET,
        url,
        json=json_response,
        status=status,
        match_querystring=False)


def get_request():
    req = RequestFactory().get('/')
    SessionMiddleware().process_request(req)
    req.session.save()
    return req


def setup_access_token_responses():
    """
    We assume that we have hooked up the app correctly and have correct
    APP_ID and APP_SECRET in our local_settings.

    """
    url = (f'{settings.API_BASE_URL}/oauth/access_token?'
           f'client_id={settings.APP_ID}&'
           f'client_secret={settings.APP_SECRET}&'
           f'grant_type=client_credentials')
    responses.add(
        responses.GET,
        url,
        json={'access_token': 'test-access-token'},
        status=200)


def setup_debug_token_responses_success():
    """
    We assume that the user gave a valid Facebook user access token.

    Facebook would then return some data about that token. The part that
    interests us is the facebook `user_id`.

    """
    url = (f'{settings.API_BASE_URL}/debug_token?'
           f'input_token=test-user-token&'
           f'access_token=test-access-token')
    responses.add(
        responses.GET,
        url,
        json={'data': {
            'user_id': 'test-fb-user-id'
        }},
        status=200)


def setup_debug_token_responses_error():
    """
    We assume that the user provided an invalid Facebook user access token.

    In this case, Facebook will return something that contains the key
    `error`. If we find that key, we don't want to login the user!

    """
    url = (f'{settings.API_BASE_URL}/debug_token?'
           f'input_token=test-user-token&'
           f'access_token=test-access-token')
    responses.add(
        responses.GET,
        url,
        json={
            'data': {
                'user_id': 'something'
            },
            'error': 'Oh Oh!'
        },
        status=200)


def custom_success_handler(request, user):
    login(request, user)
    return json.dumps({'extra': 'token'})
