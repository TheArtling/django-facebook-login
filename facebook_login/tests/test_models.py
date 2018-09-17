import pytest
from mixer.backend.django import mixer

from .. import models

pytestmark = pytest.mark.django_db


class TestFacebookAccount(object):

    def test_model(self):
        obj = mixer.blend('facebook_login.FacebookAccount')
        assert obj.pk, ('Should save an instance')

    def test_str(self):
        user = mixer.blend('auth.User', email='test@example.com')
        obj = mixer.blend('facebook_login.FacebookAccount', user=user)
        result = str(obj)
        expected = str(user)
        assert result == expected, ('Should return the user email')
