import pytest

from .. import exceptions


class TestAccessTokenException:

    def test_exception(self):
        ex = exceptions.AccessTokenException()
        assert 'Error retrieving' in str(ex)


class TestDebugTokenException:

    def test_exception(self):
        ex = exceptions.DebugTokenException({})
        assert 'Unable to' in str(ex)

        ex = exceptions.DebugTokenException({'message': 'Foo'})
        assert str(ex) == 'Foo'


class TestUserEmailException:

    def test_exception(self):
        ex = exceptions.UserEmailException()
        assert 'Email access' in str(ex)


class TestFacebookRequestException:

    def test_exception(self):
        ex = exceptions.FacebookRequestException({})
        assert 'Unknown error' in str(ex)

        ex = exceptions.FacebookRequestException({'message': 'Foo'})
        assert str(ex) == 'Foo'


class TestFacebookNetworkException:

    def test_exception(self):
        ex = exceptions.FacebookNetworkException()
        assert 'Unable to' in str(ex)
