import pytest
from mixer.backend.django import mixer

from .. import models

pytestmark = pytest.mark.django_db


class TestFacebookAccount(object):

    def test_model(self):
        obj = mixer.blend('facebook_login.FacebookAccount')
        assert obj.pk, ('Should save an instance')
