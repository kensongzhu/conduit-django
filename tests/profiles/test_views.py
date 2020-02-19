import pytest
from django.shortcuts import reverse

from conduit.apps.authentication.models import User


@pytest.mark.django_db
def test_get_profile(drf_client):
    user = User.objects.create_user(username="foo", email="foo@example.org", password="pass123456")

    url = reverse('profiles:profile-detail', args=(user.username,))
    resp = drf_client.get(url)
    profile = resp.json()['profile']

    assert profile['username'] == user.username
