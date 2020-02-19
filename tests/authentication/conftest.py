import pytest

from conduit.apps.authentication.backends import JWTAuthentication


@pytest.fixture(scope='module')
def jwt_backend():
    backend = JWTAuthentication()
    yield backend
