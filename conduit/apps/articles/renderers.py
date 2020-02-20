from conduit.apps.core.renderers import ConduitJSONRender


class ArticleJSONRenderer(ConduitJSONRender):
    object_label = 'article'
    object_label_plural = 'articles'
