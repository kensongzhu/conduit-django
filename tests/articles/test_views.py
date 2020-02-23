import json

import factory
import pytest
from django.shortcuts import reverse
from django.utils.text import slugify

from ..factories import UserFactory, ProfileFactory, ArticleFactory, CommentFactory


@pytest.mark.django_db
class TestArticlesViews(object):

    @pytest.mark.django_db
    def test_create_article(self, drf_client):
        profile = ProfileFactory(user__username='foo')
        drf_client.credentials(HTTP_AUTHORIZATION='Token ' + profile.user.token)

        # payload
        article_dict = factory.build(dict, FACTORY_CLASS=ArticleFactory, author=profile)
        article_dict.pop('author')
        article_dict.pop('slug')

        data = json.dumps({
            'article': article_dict
        })

        # url
        url = reverse('articles:article-list')

        resp = drf_client.post(url, data=data, content_type="application/json")
        print(resp.json())
        actual = resp.json()['article']

        assert actual['title'] == article_dict['title']
        # this will be broken if `len(title)` > 255
        assert slugify(article_dict['title']) in actual['slug']
        assert actual['body'] == article_dict['body']
        assert actual['description'] == article_dict['description']

    @pytest.mark.django_db
    def test_list_articles(self, drf_client):
        ArticleFactory.create_batch(size=10, author=ProfileFactory(user__username='author1'))
        ArticleFactory.create_batch(size=5, author=ProfileFactory(user__username='author2'))

        url = reverse('articles:article-list')
        resp = drf_client.get(url)
        actual = resp.json()['articles']

        assert len(actual) == 15

    @pytest.mark.django_db
    def test_get_articles_by_slug(self, drf_client):
        articles = ArticleFactory.create_batch(size=5, author=ProfileFactory(user__username='author1'))
        first = articles[0]

        url = reverse('articles:article-detail', args=(first.slug,))

        resp = drf_client.get(url)
        actual = resp.json()['article']

        assert actual['title'] == first.title
        assert actual['slug'] == first.slug
        assert actual['body'] == first.body
        assert actual['description'] == first.description

    @pytest.mark.django_db
    def test_update_article(self, drf_client):
        profile = ProfileFactory(user__username='foo')
        articles = ArticleFactory.create_batch(size=5, author=profile)
        first = articles[0]

        url = reverse('articles:article-detail', args=(first.slug,))
        drf_client.credentials(HTTP_AUTHORIZATION='Token ' + profile.user.token)

        data = {
            'article': {
                "description": "foo's description"
            }
        }

        resp = drf_client.put(url, json.dumps(data), content_type="application/json")

        actual = resp.json()['article']

        assert actual['description'] == "foo's description"


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
