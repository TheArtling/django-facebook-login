import pytest
import responses

from django.contrib.auth.models import User
from mixer.backend.django import mixer

from . import utils as test_utils
from .. import settings
from .. import auth_backends
from .. import models
from .. import exceptions

pytestmark = pytest.mark.django_db

URLS = test_utils.URLS


class TestFacebookAuthBackend:

    def test_authenticate_none(self):
        backend = auth_backends.FacebookAuthBackend()
        req = test_utils.get_request()

        res = backend.authenticate(req, token=None)
        assert res is None, ('Should return `None`, if no token is given')

    @responses.activate
    def test_authenticate_bad_token(self):
        test_utils.add_response(URLS['access'], {'access_token': 'asd'})
        test_utils.add_response(URLS['debug'],
                                {'error': {
                                    'message': 'Bad Token'
                                }})
        backend = auth_backends.FacebookAuthBackend()
        req = test_utils.get_request()

        with pytest.raises(exceptions.FacebookRequestException):
            backend.authenticate(req, token='test-user-token')

    @responses.activate
    def test_authenticate_no_email_permission(self):
        test_utils.add_response(URLS['access'], {'access_token': 'asd'})
        test_utils.add_response(URLS['debug'], {'data': {'user_id': '123'}})
        test_utils.add_response(URLS['me'], {'id': '123'})
        backend = auth_backends.FacebookAuthBackend()
        req = test_utils.get_request()

        with pytest.raises(exceptions.UserEmailException):
            result = backend.authenticate(req, token='test-user-token')

    @responses.activate
    def test_authenticate_known_facebook_user(self):
        fb_user_id = '123'
        test_utils.add_response(URLS['access'], {'access_token': 'asd'})
        test_utils.add_response(URLS['debug'],
                                {'data': {
                                    'user_id': fb_user_id
                                }})
        test_utils.add_response(URLS['me'], {'email': 'test@example.com'})
        backend = auth_backends.FacebookAuthBackend()
        req = test_utils.get_request()

        user = mixer.blend('auth.User', email='test@example.com')
        fb_account = mixer.blend(
            'facebook_login.FacebookAccount', user=user, fb_user_id=fb_user_id)

        result = backend.authenticate(req, token='test-user-token')
        assert result == user, (
            'Should return the Django user that has the same email as the'
            ' given Facebook user')
        assert models.FacebookAccount.objects.all().count() == 1, (
            'Should create a FacebookAccount instance')
        assert models.FacebookAccount.objects.all()[0].user == user, (
            'Should tie FacebookAccount instance to Django user')

    @responses.activate
    def test_authenticate_connect_fb_user_with_known_django_user(self):
        test_utils.add_response(URLS['access'], {'access_token': 'asd'})
        test_utils.add_response(URLS['debug'], {'data': {'user_id': '123'}})
        test_utils.add_response(URLS['me'], {'email': 'test@example.com'})
        backend = auth_backends.FacebookAuthBackend()
        req = test_utils.get_request()

        user = mixer.blend('auth.User', email='test@example.com')
        result = backend.authenticate(req, token='test-user-token')
        assert result == user, ('Should return the Django user ')

    @responses.activate
    def test_authenticate_signup_completely_unknown_user(self):
        test_utils.add_response(URLS['access'], {'access_token': 'asd'})
        test_utils.add_response(URLS['debug'], {'data': {'user_id': '123'}})
        test_utils.add_response(URLS['me'], {'email': 'test@example.com'})
        backend = auth_backends.FacebookAuthBackend()
        req = test_utils.get_request()

        result = backend.authenticate(req, token='test-user-token')
        assert User.objects.all().count() == 1, (
            'Should create new Django user')
        assert models.FacebookAccount.objects.all().count() == 1, (
            'Should create new FacebookAccount')
        assert models.FacebookAccount.objects.all()[
            0].user == User.objects.all()[0], (
                'Should tie new instances together')

    def test_get_user(self):
        backend = auth_backends.FacebookAuthBackend()
        user = mixer.blend('auth.User')
        res = backend.get_user(666)
        assert res is None, (
            'Should return `None` when an unknown user-id was provided')

        res = backend.get_user(user.pk)
        assert res == user, ('Should return the user for the given PK')
