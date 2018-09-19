import requests

from django.contrib.auth import authenticate, login
from django.utils.module_loading import import_string

from . import settings


def success_handler_default(request, user):
    """
    Logs in the user that has been queried or created by the
    FacebookAuthMutation.

    """
    login(request, user)
    return None


def success_handler(request, user):  # pragma: nocover
    # too trivial to test
    """Imports and then calls the success handler function."""
    success_handler_func = import_string(settings.SUCCESS_HANDLER)
    return success_handler_func(request, user)


def get_app_access_token():
    """
    Gets an access token from Facebook.

    We need this token in order to make more Facebook API requests.

    """
    resp = requests.get(f'{settings.API_BASE_URL}/oauth/access_token?'
                        f'client_id={settings.APP_ID}&'
                        f'client_secret={settings.APP_SECRET}&'
                        f'grant_type=client_credentials').json()
    return resp['access_token']


def debug_token(user_access_token, app_access_token):
    """
    Validates a given user access token and returns user information.

    On the client, the Facebook login returns a userID and a token. We only
    need the userID to hook it up with our own user model but we need to verify
    that the token that the client has sent us is indeed valid, otherwise
    anyone could impersonate anyone by just sending us their Facebook userID.

    """
    resp = requests.get(f'{settings.API_BASE_URL}/debug_token?'
                        f'input_token={user_access_token}&'
                        f'access_token={app_access_token}')
    return resp.json()


def get_user_email(user_access_token):
    """
    Given a valid user access token, it will return the user's email.

    """
    resp = requests.get(f'{settings.API_BASE_URL}/me?'
                        f'access_token={user_access_token}&fields=email')
    return resp.json().get('email', None)
