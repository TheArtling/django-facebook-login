import pytest
import responses

from . import utils
from .. import schema

pytestmark = pytest.mark.django_db

URLS = utils.URLS


class TestFacebookAuthMutation:

    def test_mutate_no_token(self):
        m = schema.FacebookAuthMutation()
        info = utils.InfoFactory()
        res = m.mutate(None, info)
        assert res.status == 400, ('Should return 400 if no token was given')

    @responses.activate
    def test_mutate_bad_token(self):
        m = schema.FacebookAuthMutation()
        info = utils.InfoFactory()

        utils.add_response(URLS['access'], {'access_token': 'asd'})
        utils.add_response(URLS['debug'], {'error': {'message': 'Bad token'}})
        res = m.mutate(None, info, access_token='bad-token')
        assert res.status == 400, ('Should return 400 if bad token was given')

    @responses.activate
    def test_mutate_valid_token(self):
        m = schema.FacebookAuthMutation()
        info = utils.InfoFactory()

        utils.add_response(URLS['access'], {'access_token': 'asd'})
        utils.add_response(URLS['debug'], {'data': {'user_id': '123'}})
        utils.add_response(URLS['me'], {'email': 'test@example.com'})
        res = m.mutate(None, info, access_token='test-token')
        assert res.status == 200, (
            'Should return 200 if the Facebook login succeeded')
        assert res.extra is None, (
            'Should return None if success handler not specified')

    @responses.activate
    def test_custom_success_handler_with_extra_data(self):
        # monkeypatching the setting
        from facebook_login import settings
        old = settings.SUCCESS_HANDLER
        settings.SUCCESS_HANDLER = 'facebook_login.tests.utils.custom_success_handler'

        m = schema.FacebookAuthMutation()

        utils.add_response(URLS['access'], {'access_token': 'asd'})
        utils.add_response(URLS['debug'], {'data': {'user_id': '123'}})
        utils.add_response(URLS['me'], {'email': 'test@example.com'})
        info = utils.InfoFactory()

        res = m.mutate(
            None, info, email='test@example.com', access_token='test-token')

        assert res.status == 200, (
            'Should return 200 if the Facebook login succeeded')

        assert 'token' in res.extra, (
            'Should return extra data from success handler')

        # undo monkeypatching
        settings.SUCCESS_HANDLER = old
