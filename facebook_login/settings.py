from django.conf import settings

# Mandatory settings that have to be provided by the user:
APP_ID = settings.FB_LOGIN_APP_ID
APP_SECRET = settings.FB_LOGIN_APP_SECRET

# Optional settings that can be overridden by the user:
GRAPH_VERSION = getattr(settings, 'FB_LOGIN_GRAPH_VERSION', 'v5.0')

API_BASE_URL = getattr(settings, 'FB_LOGIN_API_BASE_URL',
                       f'https://graph.facebook.com/{GRAPH_VERSION}')

ERROR_HANDLER = getattr(settings, 'FB_LOGIN_ERROR_HANDLER',
                        'facebook_login.utils.error_handler_default')

SUCCESS_HANDLER = getattr(settings, 'FB_LOGIN_SUCCESS_HANDLER',
                          'facebook_login.utils.success_handler_default')
