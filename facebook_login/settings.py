from django.conf import settings

# Mandatory settings that have to be provided by the user:
APP_ID = settings.FB_LOGIN_APP_ID
APP_SECRET = settings.FB_LOGIN_APP_SECRET

# Optional settings that can be overridden by the user:
API_BASE_URL = getattr(settings, 'FB_LOGIN_API_BASE_URL',
                       'https://graph.facebook.com/v3.1')

SUCCESS_HANDLER = getattr(settings, 'FB_LOGIN_SUCCESS_HANDLER',
                          'facebook_login.utils.success_handler_default')
