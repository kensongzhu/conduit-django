import json

import pytest
from django.urls import reverse

from conduit.apps.authentication.models import User


@pytest.mark.django_db
class TestAuthenticationAPI(object):

    def test_register_new_user(self, client):
        url = reverse('authentication:registration')

        data = {
            'username': 'foo',
            'email': 'foo@example.org',
            'password': 'secret123'
        }

        resp = client.post(url, data=data, content_type='application/json')
        actual = resp.json()

        assert resp.status_code == 201
        assert actual['user']['username'] == data['username']
        assert actual['user']['email'] == data['email']

    @pytest.mark.parametrize(
        'email, password', [
            ('foo@example.org', 'secret123'),
            ('bar@example.org', 'secret123'),
        ]
    )
    def test_user_login(self, client, email, password):
        User.objects.create_user(username='foo', email='foo@example.org', password='secret123')

        url = reverse('authentication:login')

        data = {
            'email': email,
            'password': password
        }

        resp = client.post(url, data=data, content_type='application/json')
        actual = resp.json()

        if 'user' in actual:
            assert resp.status_code == 200
            assert actual['user']['email'] == data['email']
        else:
            assert 'not found' in actual['errors']['error'][0]

    def test_get_user(self, drf_client):
        user = User.objects.create_user(username='foo', email='foo@example.org', password='secret123')
        # Basic Auth
        # drf_client.login(username='foo@example.org', password='secret123')

        # Token Auth
        drf_client.credentials(HTTP_AUTHORIZATION='Token ' + user.token)

        url = reverse('authentication:user-detail')

        resp = drf_client.get(url)
        assert resp.status_code == 200
        actual = resp.json()

        assert actual['user']['username'] == 'foo'
        assert actual['user']['email'] == 'foo@example.org'

    def test_update_user(self, drf_client):

        user = User.objects.create_user(username='foo', email='foo@example.org', password='secret123')
        # Basic Auth
        # drf_client.login(username='foo@example.org', password='secret123')

        # Token Auth
        drf_client.credentials(HTTP_AUTHORIZATION='Token ' + user.token)

        url = reverse('authentication:user-detail')

        data = {'user': {
            "username": "bar",
            "email": "bar@example.org",
            "password": "admin123456"
        }}

        resp = drf_client.put(url, data=json.dumps(data), content_type="application/json")
        actual = resp.json()['user']
        user.refresh_from_db()

        assert User.objects.count() == 1
        assert actual['username'] == 'bar'
        assert actual['email'] == 'bar@example.org'
        assert user.check_password('admin123456')
