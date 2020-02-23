import json

from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from tests.models import DummyModel
from tests.serializers import DummySerializer


# Views
class ValidationErrorView(APIView):

    def get(self, request, *args, **kwargs):
        DummySerializer(data={}).is_valid(raise_exception=True)


class NotFoundErrorView(generics.RetrieveAPIView, generics.GenericAPIView):
    queryset = DummyModel.objects.all()
    serializer_class = DummySerializer

    def get(self, request, *args, **kwargs):
        raise NotFound('not found')


# helpers
def render_as_json(response):
    rendered = JSONRenderer().render(response.data).decode('utf-8')
    return json.loads(rendered)


class TestCoreExceptionHandlers(object):

    def test_handle_generic_validation_errors(self, drf_rf):
        view = ValidationErrorView.as_view()

        request = drf_rf.get('/', content_type='application/json')

        resp = view(request)

        result = render_as_json(resp)

        expected_data = {'errors': {'name': ['This field is required.']}}

        assert result == expected_data

    def test_handle_not_found_errors(self, drf_rf):
        view = NotFoundErrorView.as_view()

        request = drf_rf.get('/', content_type='application/json')

        resp = view(request)

        result = render_as_json(resp)

        expected_data = {'errors': {'dummy model': 'not found'}}

        assert expected_data == result
