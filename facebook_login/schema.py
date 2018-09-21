from builtins import str
from builtins import object
import graphene
import json
import requests

from django.contrib.auth import authenticate, get_user_model

from .models import FacebookAccount
from . import utils


class FacebookAuthMutation(graphene.Mutation):

    class Arguments(object):
        access_token = graphene.String()

    status = graphene.Int()
    form_errors = graphene.String()
    extra = graphene.String()

    @staticmethod
    def mutate(root, info, **args):
        user_access_token = args.get('access_token')

        if user_access_token is None:
            return FacebookAuthMutation(
                status=400,
                form_errors=json.dumps({
                    'facebook': ['No user access token was provided']
                }),
                extra=None,
            )

        try:
            user = authenticate(request=info.context, token=user_access_token)
        except Exception as ex:
            return utils.error_handler(FacebookAuthMutation, info.context, ex)

        extra = utils.success_handler(info.context, user)

        return FacebookAuthMutation(status=200, form_errors=None, extra=extra)


class Mutation(object):
    facebook_auth = FacebookAuthMutation.Field()
