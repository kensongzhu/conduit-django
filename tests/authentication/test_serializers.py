from copy import deepcopy

import pytest

from conduit.apps.authentication.models import User
from conduit.apps.authentication.serializers import UserSerializer


@pytest.mark.django_db
class TestSerializers(object):

    def test_user_serializer_update(self):
        instance = User.objects.create_user(username='foo', email='foo@example.org', password='pass123456')
        data = {'username': 'bar', 'email': 'bar@example.org', 'password': 'pass654321'}

        serializer = UserSerializer()
        actual = serializer.update(instance=instance, validated_data=deepcopy(data))

        assert actual.username == data['username']
        assert actual.email == data['email']
        assert actual.check_password(data['password'])
