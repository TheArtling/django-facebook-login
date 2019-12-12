# Django Facebook Login

`django-facebook-login` provides an authentication backend and a GraphQL mutation
that takes a Facebook user-access-token and the user's email and then does one
of the following:

- Sign-up new user
- Connect existing Django user with their Facebook account
- Login existing, already connected Django user

In all cases, the user will be authenticated afterwards. This means, unlike
most other custom authentication backends, this backend will create a new
user if the given credentials (Facebook email + Facebook user access token)
are not known, yet.

Make sure you read the `Noteworthy Things` below before you decide to use this
library.

# Quick start

1.  Add "facebook-login" to your INSTALLED_APPS setting like this:

    ```py
    INSTALLED_APPS = [
        ...
        'facebook-login',
    ]
    ```

1.  Add the `FacebookAuthBackend` to your `AUTHENTICATION_BACKENDS` setting:

    ```py
    AUTHENTICATION_BACKENDS = (
        ...,
        "facebook_login.auth_backends.FacebookAuthBackend",
    )
    ```

1.  Hook up the mutation in your GraphQL schema:

    ```py
    # in your main `schema.py`:
    import graphene
    from facebook_login import schema as fb_login

    class Mutation(
        ...
        fb_login.Mutation,
        graphene.ObjectType,
    ):
        pass

    class Queries(...):
        pass

    schema = graphene.Schema(query=Queries, mutation=Mutation)
    ```

1.  Run `python manage.py migrate` to create the `FacebookAccount` table.

1.  Configure the app in your `local_settings.py`:

    ```
    # Get these values from https://developers.facebook.com/apps/
    FB_LOGIN_APP_ID = 'YOUR APP ID'
    FB_LOGIN_APP_SECRET = 'YOUR APP SECRET'
    ```

# Noteworthy things

## This library does not include frontend code

You still need extra code on your frontend that retrieves the user
access token from Facebook. Usually you would hook up the official Facebook
login button that triggers the official Facebook login popup and then write
some code that sends the token that was returned by Facebook to our mutation.

## This library forces the user to grant access to their Facebook email

During the official Facebook login popup, the user can decide to revoke access
to the email address. Other libraries, like django-allauth will have some extra
views where the user is then asked to enter an email anyways, after the Facebook
login. We do not care about this. Instead, we will ask the user to press the
login button again and this time please grant access to the email address.

## This library does not return a JWT token or anything like it

Please note that we don't use JWT in our projects. We use Django's default
session based authentication. Therefore, our mutation does not return anything.

Our mutation does call Django's `login()` function, which will save the new
login-state into the user's session. When the mutation returns, it will instruct
the browser to save the new session key in the cookie. Our frontend will then
trigger a `window.location = /new/url/`, since this is a new request (including
the new session key), the server-rendered response will realize that this is a
now logged-in user.

If you would like to disable this behavior, you may provide a custom function
for the `FB_LOGIN_SUCCESS_HANDLER` setting (see below).

# Configuration

This app uses the following settings:

## FB_LOGIN_APP_ID (mandatory)

This should be your Facebook app-id.

## FB_LOGIN_APP_SECRET (mandatory)

This should be your Facebook app secret.

## FB_LOGIN_GRAPH_VERSION (optional)

**Default**: `'v5.0'`

You can set this to a higher version in order to stay compliant with the
Facebook guidelines. Of course, just bumping the version number does not
guarantee that this app will still work, but the APIs that we use here have
been pretty stable for years, so it might just work.

## FB_LOGIN_SUCCESS_HANDLER (optional)

**Default**: `facebook_login.utils.success_handler_default`

Set this to your own function in case you need to do additional things
when a user logs in. You can find our original implementation in `utils.success_handler_default()`.

Your custom function may return a string and that string would be passed on
to the frontend by the mutation as the `extra` key. You will most likely want
to return something like this: `json.dumps({'token': 'ABC123...'})`.
If you do return something (i.e. a JWT token), then the mutation will return
it to the frontend as the `extra` key.

## FB_LOGIN_ERROR_HANDLER (optional)

**Default**: `facebook_login.utils.error_handler_default`

Set this to your own function, for example if you would like to log certain
exceptions to Sentry or alert you in other ways when Facebook login attempts
are crashing. By default, only the user will see error messages on the frontend
but you will likely not notice that something is wrong.

Your implementation should look something like this:

```
from facebook_login import exceptions

def error_handler_custom(facebook_auth_mutation, request, exception):
    message = ''
    if isinstance(exception, exceptions.UserEmailException):
        message = str(exception)
    else:
        message = ('Failed to login with Facebook. Our engineers have been'
                   ' notified. Please try again, later.')

    # log exception to Sentry

    return facebook_auth_mutation(
        status=400,
        form_errors=json.dumps({
            'facebook': [message]
        }),
        extra=None,
    )
```

As you can see, this way you can customize the error messages that are shown
to the user and you can use any logging service that you like.

## FB_LOGIN_API_BASE_URL (optional)

**Default**: `'https://graph.facebook.com/v3.1'`

Allows to override the base API URL, just in case. Of course, we are not sure,
if a future API would be backwards compatible, so just changing this to a higher
API version number might cause issues with this library.

# Troubleshooting

## KeyError: 'password'

If this happens, chances are that you are using `django-allauth`. Their
authentication backend crashes when Django's `authenticate()` function is
called without a `username` and `password` keyword-argument. As a workaround,
you can just make sure that `facebook_login.auth_backends.FacebookAuthBackend`
appears before other authentication backends.

# Contributing

- Clone this repo
- `mkvirtualenv --python=python3.6 django-facebook-login`
- `pip install -r requirements.txt`
- `pip install -r test_requirements.txt`
- `fab test`
- `open htmlcov/index.html`
- `./manage.py migrate` # This creates a sqlite3 DB
- `./manage.py createsuperuser`
- `./manage.py runserver`

Unfortunately, running the local devserver only gives you access to the Django
admin. There is no demo-frontend code that would actually call this library's
backend code, yet.

# Acknowledgements

This library was built with love at [The Artling](https://theartling.com)
