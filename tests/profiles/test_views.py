import pytest
from django.shortcuts import reverse

from ..factories import UserFactory


@pytest.mark.django_db
class TestProfileViews(object):

    @pytest.mark.django_db
    def test_unauthenticated_user_get_profile(self, drf_client):
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

    def test_authenticate_user_get_profile(self, drf_auth_client):
        user_foo = UserFactory.create(username="foo")

        # follow the user `foo`
        drf_auth_client.user.profile.follow(user_foo.profile)

        url = reverse('profiles:profile-detail', args=(user_foo.username,))
        resp = drf_auth_client.get(url)
        profile = resp.json()['profile']

        assert profile["following"]

    def test_auth_user_follow_other_profile(self, drf_auth_client):
        user = UserFactory(username='foo')

        url = reverse('profiles:profile-follow', args=(user.username,))

        resp = drf_auth_client.post(url)
        profile = resp.json()['profile']

        assert profile['username'] == user.username
        assert profile['following']

    def test_auth_user_unfollow_other_profile(self, drf_auth_client):
        user = UserFactory(username='foo')

        # follow first
        drf_auth_client.user.profile.follow(user.profile)
        url = reverse('profiles:profile-follow', args=(user.username,))

        resp = drf_auth_client.delete(url)
        profile = resp.json()['profile']

        assert profile['username'] == user.username
        assert not profile['following']

    def test_raise_validation_error_follow_self(self, drf_auth_client):
        url = reverse('profiles:profile-follow', args=(drf_auth_client.user.username,))

        resp = drf_auth_client.post(url)
        errors = resp.json()["errors"]

        assert "You can't follow yourself." in errors[0]
