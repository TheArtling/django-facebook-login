from builtins import str
from builtins import object
import graphene
import json
import requests

from django.contrib.auth import authenticate, get_user_model

from .models import FacebookAccount
from .utils import debug_token, get_app_access_token, success_handler


class FacebookAuthMutation(graphene.Mutation):

    class Arguments(object):
        email = graphene.String()
        access_token = graphene.String()

    status = graphene.Int()
    form_errors = graphene.String()
    extra = graphene.types.json.JSONString()

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
                extra=None,
            )

        user = authenticate(
            request=info.context, email=email, token=user_access_token)
        if user is None:
            return FacebookAuthMutation(
                status=400,
                form_errors=json.dumps({
                    'facebook': ['Facebook login failed.']
                }),
                extra=None,
            )

        extra = success_handler(info.context, user)
        print(extra)
        extra = json.dumps(extra) if extra else None

        return FacebookAuthMutation(status=200, form_errors=None, extra=extra)


class Mutation(object):
    facebook_auth = FacebookAuthMutation.Field()
