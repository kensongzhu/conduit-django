import pytest
from django.shortcuts import reverse

from ..factories import UserFactory


@pytest.mark.django_db
class TestProfileViews(object):

    @pytest.mark.django_db
    def test_user_get_profile(self, drf_client):
        user_foo = UserFactory.create(
            username="foo",
            email="foo@example.org",
            password="pass123456",
            profile__bio="foo's bio",
            profile__image='https://foo.png'
        )

        url = reverse('profiles:profile-detail', args=(user_foo.username,))
        resp = drf_client.get(url)
        profile = resp.json()['profile']

        assert profile['username'] == user_foo.username
        assert profile['bio'] == "foo's bio"
        assert profile['image'] == 'https://foo.png'
        # anonymous user's following default false
        assert not profile['following']
