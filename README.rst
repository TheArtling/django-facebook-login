==============
Facebook Login
==============

django-facebook-login provides a GraphQL mutation that takes a Facebook
user-access-token and the user's email and then does one of the following:

* Sign-up new user
* Connect existing Django user with their Facebook account
* Login existing, already connected Django user

In all cases, the user will be authenticated afterwards. This means, unlike
most other custom authentication backends, this backend will create a new
user if the given credentials (Facebook email + Facebook user access token)
are not known, yet.

Note that you still need extra code on your frontend that retrieves the user
access token from Facebook (i.e. the official Facebook login button).

Also note that this module assumes that the user has granted access to the
Facebook email. If a user disabled the email permission in the Facebook login
popup, this mutation will not work. You will need to show an error message
on the frontend and ask the user to try again, but this time please grant
the email permission.

Finally, please note that we don't use JWT in our projects. We use Django's
normal session based auth. Therefore, our mutation does not return anything.
You could easily write your own `CustomFacebookAuthMutation`, copy all our
code but after the `success_handler()` call you could do something else with
the user, i.e. create a JWT token and return it.

Quick start
-----------

1. Add "facebook-login" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'facebook-login',
    ]

1. Add the `FacebookAuthBackend` to your `AUTHENTICATION_BACKENDS` setting::

    AUTHENTICATION_BACKENDS = (
        ...,
        "facebook_login.auth_backends.FacebookAuthBackend",
    )


1. Hook up the mutation in your GraphQL schema::

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


1. Run `python manage.py migrate` to create the FacebookAccount table.

1. Configure the app in your `local_settings.py`::

   # Get these values from https://developers.facebook.com/apps/
   FB_LOGIN_APP_ID = 'YOUR APP ID'
   FB_LOGIN_APP_SECRET = 'YOUR APP SECRET'


Configuration
-------------

This app uses the following settings:

**FB_LOGIN_SUCCESS_HANDLER**

Default: `facebook_login.utils.success_handler`


**FB_LOGIN_API_BASE_URL**

Default: `'https://graph.facebook.com/v3.1'`

Troubleshooting
---------------

**KeyError: 'password'**

If this happens, chances are that you are using `django-allauth`. Their
authentication backend crashes when Django's `authenticate()` function is
called without a `username` and `password` keyword-argument. As a workaround,
you can just make sure that `facebook_login.auth_backends.FacebookAuthBackend`
appears before other authentication backends.
