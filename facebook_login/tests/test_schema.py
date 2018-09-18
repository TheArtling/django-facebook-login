import pytest
import responses

from . import utils
from .. import schema

pytestmark = pytest.mark.django_db


class TestFacebookAuthMutation:

    @responses.activate
    def test_mutate(self):
        m = schema.FacebookAuthMutation()
        utils.setup_access_token_responses()
        utils.setup_debug_token_responses_success()
        info = utils.InfoFactory()
        res = m.mutate(None, info)
        assert res.status == 400, ('Should return 400 if no email was given')

        res = m.mutate(None, info, email='test@example.com')
        assert res.status == 400, (
            'Should return 400 if the Facebook login failed (i.e. becuase no'
            ' token or an invalid token was given)')

        res = m.mutate(
            None, info, email='test@example.com', access_token='test-token')

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
        utils.setup_access_token_responses()
        utils.setup_debug_token_responses_success()
        info = utils.InfoFactory()

        res = m.mutate(
            None, info, email='test@example.com', access_token='test-token')

        assert res.status == 200, (
            'Should return 200 if the Facebook login succeeded')

        assert 'token' in res.extra, (
            'Should return extra data from success handler')

        # undo monkeypatching
        settings.SUCCESS_HANDLER = old
