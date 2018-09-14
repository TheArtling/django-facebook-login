from builtins import str
from builtins import object
import graphene
import json
import requests
import uuid

from django.conf import settings
from django.contrib.auth.models import User

from allauth.socialaccount.models import SocialAccount
from rest_framework_jwt.settings import api_settings

FACEBOOK_API_BASE_URL = 'https://graph.facebook.com/v3.1'


def get_app_access_token():
    """
    Gets an access token from Facebook.

    We need this token in order to make more Facebook API requests.

    """
    resp = requests.get(f'{FACEBOOK_API_BASE_URL}/oauth/access_token?'
                        f'client_id={settings.FACEBOOK_APP_ID}&'
                        f'client_secret={settings.FACEBOOK_APP_SECRET}&'
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
    resp = requests.get(f'{FACEBOOK_API_BASE_URL}/debug_token?'
                        f'input_token={user_access_token}&'
                        f'access_token={app_access_token}')
    return resp.json()


class FacebookAuthMutation(graphene.Mutation):

    class Arguments(object):
        user_id = graphene.String()
        email = graphene.String()
        access_token = graphene.String()
        signed_request = graphene.String()

    status = graphene.Int()
    form_errors = graphene.String()
    token = graphene.String()

    @staticmethod
    def mutate(root, info, **args):
        user_access_token = args.get('access_token')
        email = args.get('email')

        if not email:
            return FacebookAuthMutation(
                status=400,
                form_errors=json.dumps({
                    'facebook': [
                        'Facebook login failed. You have not granted access to'
                        ' your email address.'
                    ]
                }),
                token=None)

        app_access_token = get_app_access_token()
        token_info = debug_token(user_access_token, app_access_token)
        if token_info.get('error'):
            return FacebookAuthMutation(
                status=400,
                form_errors=json.dumps({
                    'facebook': [
                        token_info['error']['message'],
                    ]
                }),
                token=None)

        user_id = token_info['data']['user_id']

        user = None
        socialaccount = None
        try:
            socialaccount = SocialAccount.objects.get(
                uid=user_id, provider='facebook')
            user = socialaccount.user
        except SocialAccount.DoesNotExist:
            pass

        if user is None and socialaccount is None:
            try:
                user = User.objects.get(email=email)
                SocialAccount.objects.filter(
                    user=user, provider='facebook').delete()
                socialaccount = SocialAccount.objects.create(
                    user=user, uid=user_id, provider='facebook')
            except User.DoesNotExist:
                pass

        if user is None and socialaccount is None:
            user = User.objects.create(
                username=str(uuid.uuid4()), email=args.get('email'))
            socialaccount = SocialAccount.objects.create(
                user=user, uid=user_id, provider='facebook')

        payload = api_settings.JWT_PAYLOAD_HANDLER(user)
        token = api_settings.JWT_ENCODE_HANDLER(payload)
        return FacebookAuthMutation(status=200, form_errors=None, token=token)


class Mutation(object):
    facebook_auth = FacebookAuthMutation.Field()
