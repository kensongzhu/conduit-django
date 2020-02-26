from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ArticleViewSet, CommentListCreateAPIView, CommentDestroyAPIView, ArticlesFavoriteAPIView,
    TagListAPIView
)

router = DefaultRouter(trailing_slash=False)
router.register(r'articles', ArticleViewSet)
app_name = 'articles'

urlpatterns = [
    path('', include(router.urls)),
    path('articles/<slug:article_slug>/comments/<int:comment_pk>', CommentDestroyAPIView.as_view(),
         name="comment-detail"),
    path('articles/<slug:article_slug>/comments', CommentListCreateAPIView.as_view(), name="comment-list"),
    path('articles/<slug:article_slug>/favorite', ArticlesFavoriteAPIView.as_view(), name='article-favorite'),
    path('tags', TagListAPIView.as_view(), name='tag-list'),

]
