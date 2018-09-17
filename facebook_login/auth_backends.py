import uuid

from django.contrib.auth import get_user_model

from .models import FacebookAccount
from .utils import debug_token, get_app_access_token


class FacebookAuthBackend:

    def authenticate(self, request, email=None, token=None):
        """
        Tries to authenticate the given email and Facebook user access token.

        NOTE: Unlike most other custom authentication backends, this backend
        will create a new user if the given email/token are not found in the
        Django DB, yet. After validating the token, we can assume that the
        email/token combination is valid, because that is what Facebook
        returned to us.

        :request: A WSGIRequest instance.
        :email: The email of the user as returned by the Facebook login popup.
        :token: The user access token as returned by the Facebook login popup.
        :returns: A User instance or `None`.

        """
        if not email or not token:
            return None
        app_access_token = get_app_access_token()
        token_info = debug_token(token, app_access_token)
        if token_info.get('error'):
            return None

        # Step1: See if we already know this Facebook user...
        user_id = token_info['data']['user_id']
        user = None
        fb_account = None
        try:
            fb_account = FacebookAccount.objects.get(fb_user_id=user_id)
            if fb_account.user:
                return fb_account.user
        except FacebookAccount.DoesNotExist:
            pass

        # Step2: Unknown FB user, see if we already know this email...
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            FacebookAccount.objects.filter(user=user).delete()
            fb_account = FacebookAccount.objects.create(
                user=user, fb_user_id=user_id)
            return user
        except User.DoesNotExist:
            pass

        # Step3: Unknown FB user and email, let's create a new user...
        user = User.objects.create(username=str(uuid.uuid4()), email=email)
        fb_account = FacebookAccount.objects.create(
            user=user, fb_user_id=user_id)
        return user

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
