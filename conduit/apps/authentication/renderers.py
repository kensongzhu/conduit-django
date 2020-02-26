from conduit.apps.core.renderers import ConduitJSONRender


class UserJSONRenderer(ConduitJSONRender):
    object_label = 'user'
    pagination_object_label = 'users'
    pagination_count_label = 'usersCount'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # If we receive a `token` as part of the response, it will be byte object
        # Byte objects don't serialize well, so we need to decode it before rendering the `User` object
        token = data.get('token', None)

        if not token and isinstance(token, bytes):
            # As mentioned above, we will decode `token` if it is type of bytes
            data['token'] = token.decode('utf-8')

        return super(UserJSONRenderer, self).render(data)
