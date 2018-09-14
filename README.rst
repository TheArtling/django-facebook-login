==============
Facebook Login
==============

django-facebook-login provides a GraphQL mutation that takes a Facebook
user-access-token and the user's email and then does one of the following:

* Create new Django user and new FacebookAccount instance
* Create new FacebookAccount instance and hook it up with existing Django user
* Detect existing Django user and FacebookAccount and create no new instances

In all cases, the user will be authenticated afterwards.

Note that you still need extra code on your frontend that retrieves the user
access token from Facebook (i.e. the official Facebook login button).

Quick start
-----------

1. Add "facebook-login" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'facebook-login',
    ]

2. Hook up the mutation in your GraphQL schema::

    TODO

3. Run `python manage.py migrate` to create the FacebookAccount table.
