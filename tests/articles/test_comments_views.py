import json

import pytest
from django.shortcuts import reverse

from ..factories import UserFactory, ArticleFactory, CommentFactory


@pytest.mark.django_db
class TestCommentsViews(object):

    def test_delete_comment(self, drf_auth_client):
        author_foo = UserFactory.create(username="foo")
        article_by_foo = ArticleFactory.create(author=author_foo.profile, slug='article-by-foo')

        commenter = UserFactory.create(username="bar")
        comment = CommentFactory.create(author=commenter.profile, article=article_by_foo)

        url = reverse("articles:comment-detail", args=(article_by_foo.slug, comment.pk))

        # TODO Bug: Any auth user can delete anyone's comment
        resp = drf_auth_client.delete(url)
        assert resp.status_code == 204

    def test_create_comment(self, drf_auth_client):
        author_foo = UserFactory.create(username="foo")
        article_by_foo = ArticleFactory.create(author=author_foo.profile, slug='article-by-foo')

        # create comment by default auth user
        url = reverse('articles:comment-list', args=(article_by_foo.slug,))
        resp = drf_auth_client.post(
            url,
            data=json.dumps({'comment': {'body': 'my comment'}}),
            content_type='application/json'
        )

        expected_data = resp.json()['comment']

        assert expected_data['author']['username'] == drf_auth_client.user.username
        assert expected_data['body'] == 'my comment'

    def test_list_comments(self, drf_client):
        # an user named `foo` and related article
        author_foo = UserFactory.create(username="foo")
        article_by_foo = ArticleFactory.create(author=author_foo.profile, slug='article-by-foo')

        # other users comment this article by foo
        commenters = UserFactory.create_batch(size=3)
        for c in commenters:
            CommentFactory.create(author=c.profile, article=article_by_foo, body="%s's comment" % c.username)

        # unauthenticated users can view the comments list of anyone's article
        url = reverse('articles:comment-list', args=(article_by_foo.slug,))
        resp = drf_client.get(url)
        expected_data = resp.json()["comments"]

        actual_commenter = sorted([c.username for c in commenters])
        expect_commenter = sorted([item['author']['username'] for item in expected_data])

        assert len(expected_data) == len(commenters)
        assert actual_commenter == expect_commenter
