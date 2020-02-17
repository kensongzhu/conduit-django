import pytest

from conduit.apps.authentication.models import User


@pytest.mark.django_db
class TestCustomUser(object):

    @pytest.mark.parametrize('username, email, password', [
        ('foo', 'foo@example.org', 'foo'),
        (None, 'foo@example.org', 'foo'),
        ('foo', None, 'foo')
    ])
    def test_custom_manager_create_user(self, username, email, password):
        if username and email:
            user = User.objects.create_user(username=username, password=password, email=email)
            assert user.username == username
            assert user.email == email

        if not username or not email:
            with pytest.raises(ValueError):
                User.objects.create_user(username=username, password=password, email=email)

    @pytest.mark.parametrize('username, email, password', [
        ('foo', 'foo@example.org', 'foo'),
        ('bar', 'bar@example.org', None)
    ])
    def test_custom_manager_create_superuser(self, username, email, password):
        if password:
            user = User.objects.create_superuser(username=username, email=email, password=password)

            assert user.is_superuser
            assert user.is_staff
            assert user.check_password(password)

        else:
            with pytest.raises(ValueError):
                User.objects.create_superuser(username=username, email=email, password=password)

    def test_user_has_jwt_token(self):
        user = User.objects.create_user('foo', 'foo@example.org', 'foo')
        assert user.token
