from conduit.apps.core.renderers import ConduitJSONRender


class ProfileJSONRenderer(ConduitJSONRender):
    object_label = 'profile'
    pagination_object_label = 'profiles'
    pagination_count_label = 'profilesCount'
