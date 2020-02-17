from datetime import datetime

import pytest
from django.urls import reverse
from rest_framework.exceptions import AuthenticationFailed

from conduit.apps.authentication.models import User
from .utils import gen_user_token


@pytest.mark.django_db
class TestJWTBackend(object):
    @pytest.mark.parametrize(
        'token, expected', [
            (None, None),
            ('Token ', None),
            ('Token with more than 1 space', None),
            ('Token abc', AuthenticationFailed('Invalid authentication'))
        ]
    )
    def test_authenticate_with_invalid_token(self, drf_rf, jwt_backend, token, expected):

        url = reverse('authentication:login')
        request = drf_rf.post(url)
        if token:
            request.META['HTTP_AUTHORIZATION'] = token

        if not isinstance(expected, AuthenticationFailed):
            assert jwt_backend.authenticate(request) is None
        else:
            # test invalid token
            with pytest.raises(AuthenticationFailed, match=str(expected)):
                jwt_backend.authenticate(request)

    def test_authenticate_finds_no_user(self, drf_rf, jwt_backend):

        url = reverse('authentication:login')
        request = drf_rf.post(url)
        request.META['HTTP_AUTHORIZATION'] = 'Token %s' % gen_user_token(1, datetime.now())

        with pytest.raises(AuthenticationFailed, match='No user'):
            jwt_backend.authenticate(request)

    def test_authenticate_deactivated_users(self, drf_rf, jwt_backend):
        user = User.objects.create_user(username='foo', email='foo@example.org', password='pass123456')
        user.is_active = False
        user.save()

        url = reverse('authentication:login')
        request = drf_rf.post(url)
        request.META['HTTP_AUTHORIZATION'] = 'Token %s' % user.token

        with pytest.raises(AuthenticationFailed, match='deactivated'):
            jwt_backend.authenticate(request)

    def test_authenticate_success(self, drf_rf, jwt_backend):
        user = User.objects.create_user(username='foo', email='foo@example.org', password='pass123456')
        url = reverse('authentication:login')
        request = drf_rf.post(url)
        request.META['HTTP_AUTHORIZATION'] = 'Token %s' % user.token

        actual_user, actual_token = jwt_backend.authenticate(request)

        assert actual_user == user
        assert actual_token == user.token
