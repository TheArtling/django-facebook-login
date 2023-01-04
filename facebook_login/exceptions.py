from django.utils.translation import gettext as _


class AccessTokenException(Exception):
    """
    Is raised when we are unable to retrieve an access token.

    This can happen either because Facebook is down or because our
    local_settings.py has wrong values for APP_ID and APP_SECRET.

    This is a severe error and means that our engineers need to fix the
    configuration.

    """

    def __str__(self):
        return _("Error retrieving access token. Please try again later.")


class DebugTokenException(Exception):
    """
    Is raised when we do get a response from Facebook but the response json
    has an `error` key.

    This would probably mean that someone is trying to attack the system by
    submitting invalid Facebook user access tokens.

    This should never happen and can probably be ignored.

    """

    def __init__(self, error):
        self.error = error

    def __str__(self):
        try:
            return self.error['message']
        except KeyError:
            return _('Unable to validate token. Please try again later.')


class UserEmailException(Exception):
    """
    Is raised when the call to `/me` does not return a value for the email.

    This would probably mean that the user disabled the email-permission.

    This could also mean that the user does not have a primary email in their
    Facebook profile, but we think this is such a rare case, this library
    can't currently handle that.

    """

    def __str__(self):
        return _(
            "Email access was not granted. Please try to login again and grant"
            " email access.")


class FacebookRequestException(Exception):
    """
    Is raised when requests return a 400 response status.

    This usually means that you provided a wrong app access token.

    This is a severe error and means that our engineers need to make sure that
    the app is properly configured.

    """

    def __init__(self, error):
        self.error = error

    def __str__(self):
        try:
            return self.error['message']
        except KeyError:
            return _("Unknown error occurred when communicating with Facebook.")


class FacebookNetworkException(Exception):
    """
    Is raised when requests returns any exception while making a request to the
    Facebook API.

    This would mean that the Facebook API is down or that our server has
    connection problems.

    This is a severe error and means that our engineers need to make sure that
    the issue is not on our side.

    """

    def __str__(self):
        return _(
            "Unable to communicate with Facebook. Please try again later.")
