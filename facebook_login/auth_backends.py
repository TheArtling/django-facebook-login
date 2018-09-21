import uuid

from django.contrib.auth import get_user_model

from .models import FacebookAccount
from .utils import debug_token, get_app_access_token, get_user_email


class FacebookAuthBackend:

    def authenticate(self, request, token=None, **kwargs):
        """
        Tries to authenticate the given Facebook user access token.

        Most auth backends require a username and a password and then checks if
        that username/password combination is correct.

        This backend is different in that it requires a Facebook user access
        token. We will then validate the token against Facebook and if the token
        is valid, we know that we have a valid user. This can be either a  new
        user or a returning user.

        That means, unlike most other custom authentication backends, this
        backend will create a new user if the given token (and it's email) are
        not found in the Django DB, yet.

        :request: A WSGIRequest instance.
        :token: The user access token as returned by the Facebook login popup.
        :kwargs: Not used. We just have this so that any kwargs passed into
          the `authenticate()` function will work and not crash this function.

        :returns: A User instance or `None`.

        """
        if not token:
            return None

        # Get app access token so we can make futher API calls
        app_access_token = get_app_access_token()

        # Use app access token to debug the user access token
        token_info = debug_token(token, app_access_token)

        # Now that the token is validated, use that token to get the email
        email = get_user_email(token)

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
