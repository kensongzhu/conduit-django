import pytest
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

from .factories import UserFactory


@pytest.fixture(scope='module')
def drf_client():
    _client = APIClient()
    yield _client


@pytest.fixture()
def drf_auth_client(db):
    _client = APIClient()

    # attached a new user to client
    _client.user = UserFactory.create(username='auth-user', password="password")

    _client.credentials(HTTP_AUTHORIZATION='Token ' + _client.user.token)

    yield _client


@pytest.fixture(scope='module')
def drf_rf():
    _factory = APIRequestFactory()
    yield _factory
