from rest_framework import serializers

from tests.models import DummyModel


# serializers
class DummySerializer(serializers.ModelSerializer):
    class Meta:
        model = DummyModel
        fields = ('id', 'name')
