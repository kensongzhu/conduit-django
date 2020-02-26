import json

from rest_framework.renderers import JSONRenderer


class ConduitJSONRender(JSONRenderer):
    charset = 'utf-8'
    object_label = 'object'
    pagination_object_label = 'objects'
    pagination_count_label = 'count'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # TODO: Bug here drop 'previous' and 'next' are left already
        if data.get('results', None) is not None:
            return json.dumps(
                {
                    self.pagination_object_label: data['results'],
                    self.pagination_count_label: data['count'],
                }
            )
        # If the view throws an error (such as the user can't be authenticated or something
        # similar), `data` will contain an `errors` key. We want the default JSONRenderer to handler rending errors
        # so we need to check for this case
        elif data.get('errors', None) is not None:
            return super(ConduitJSONRender, self).render(data)
        else:
            return json.dumps(
                {self.object_label: data}
            )
