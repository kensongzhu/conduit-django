import pytest
from django.shortcuts import reverse
from rest_framework.test import force_authenticate

from conduit.apps.articles.views import CommentListCreateAPIView
from ..factories import UserFactory, ArticleFactory


@pytest.mark.django_db
class TestCommentListCreateAPIView(object):

    def test_list_comments_by_article_slug(self, drf_rf):
        view = CommentListCreateAPIView.as_view()
        user = UserFactory.create()
        article = ArticleFactory.create(author=user.profile, slug='my-article')
        print(article.slug)

        url = reverse('articles:comment-list', args=('my-article',))
        req = drf_rf.post(url, data={'comment': {'body': 'my comment'}}, format='json')
        force_authenticate(req, user=user)

        resp = view(req, article_slug=article.slug)

        print(resp.data)

    def test_delete_comment(self):
        pass
