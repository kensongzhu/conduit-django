import json

import pytest

from conduit.apps.core.renderers import ConduitJSONRender

# core renderer
renderer = ConduitJSONRender()


@pytest.mark.django_db
class TestCoreRenderer(object):

    def test_render_single_object(self):
        data = {'id': 1, 'name': 'foo'}
        rendered = renderer.render(data)
        result = json.loads(rendered)

        assert 'object' in result
        assert result['object'] == data

    def test_render_list_objects(self):
        data_list = [{'id': 1, 'name': 'foo'}]

        data = {
            'results': data_list,
            'count': len(data_list)
        }

        rendered = renderer.render(data)
        result = json.loads(rendered)

        assert "objects" in result
        assert result["objects"] == data_list
        assert result['count'] == len(data_list)

    def test_render_errors(self):
        data = {'errors': "errors on purpose"}

        renderer.render(data)

        rendered = renderer.render(data)
        result = json.loads(rendered)

        assert result == data
