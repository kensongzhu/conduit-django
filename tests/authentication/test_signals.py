import pytest

from conduit.apps.authentication.models import User
from conduit.apps.profiles.models import Profile


@pytest.mark.django_db
def test_create_related_profile_for_user():
    user = User.objects.create_user(username="foo", email="foo@example.org", password="pass123456")

    assert user.profile.user == user
    assert Profile.objects.count() == 1

    # it should not create a new profile when user is updated
    user.username = 'bar'
    user.save()

    assert Profile.objects.count() == 1
