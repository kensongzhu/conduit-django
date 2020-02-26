from conduit.apps.core.renderers import ConduitJSONRender


class ArticleJSONRenderer(ConduitJSONRender):
    object_label = 'article'
    pagination_object_label = 'articles'
    pagination_count_label = 'articlesCount'


class CommentJSONRenderer(ConduitJSONRender):
    object_label = 'comment'
    pagination_object_label = 'comments'
    pagination_count_label = 'commentsCount'
