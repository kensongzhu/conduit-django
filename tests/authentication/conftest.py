import pytest
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

from conduit.apps.authentication.backends import JWTAuthentication


@pytest.fixture(scope='module')
def drf_client():
    _client = APIClient()
    yield _client


@pytest.fixture(scope='module')
def drf_rf():
    _factory = APIRequestFactory()
    yield _factory


@pytest.fixture(scope='module')
def jwt_backend():
    backend = JWTAuthentication()
    yield backend
