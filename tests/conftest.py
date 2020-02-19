import pytest
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory


@pytest.fixture(scope='module')
def drf_client():
    _client = APIClient()
    yield _client


@pytest.fixture(scope='module')
def drf_rf():
    _factory = APIRequestFactory()
    yield _factory
