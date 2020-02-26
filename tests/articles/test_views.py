import json
from urllib.parse import urlencode

import factory
import pytest
from django.shortcuts import reverse
from django.utils.text import slugify

from ..factories import UserFactory, ProfileFactory, ArticleFactory, CommentFactory, TagFactory

pytestmark = pytest.mark.django_db


class TestArticlesViews(object):

    def test_create_article(self, drf_auth_client):
        profile = ProfileFactory(user__username='foo')

        # payload
        tags = TagFactory.create_batch(size=5)
        tag_list = [tag.tag for tag in tags]

        article_dict = factory.build(dict, FACTORY_CLASS=ArticleFactory, author=profile, tags=(None,))
        article_dict.pop('author')
        article_dict.pop('slug')
        article_dict.pop('tags')
        article_dict.update({'tagList': tag_list})

        data = json.dumps({
            'article': article_dict
        })

        # url
        url = reverse('articles:article-list')

        resp = drf_auth_client.post(url, data=data, content_type="application/json")
        print(resp.json())
        actual = resp.json()['article']

        assert actual['title'] == article_dict['title']
        # this will be broken if `len(title)` > 255
        assert slugify(article_dict['title']) in actual['slug']
        assert actual['body'] == article_dict['body']
        assert actual['description'] == article_dict['description']
        assert sorted(actual['tagList']) == sorted(tag_list)

    def test_paginated_list_articles(self, drf_client):
        ArticleFactory.create_batch(size=20, author=ProfileFactory(user__username='author1'))
        ArticleFactory.create_batch(size=5, author=ProfileFactory(user__username='author2'))

        # assert frist page
        first_page_url = reverse('articles:article-list')
        fist_page_resp = drf_client.get(first_page_url)
        actual = fist_page_resp.json()

        assert len(actual['articles']) == 20
        assert actual['articlesCount'] == 25

        # assert next page
        next_page_url = reverse('articles:article-list') + '?' + urlencode({'offset': 20})
        next_page_resp = drf_client.get(next_page_url)
        actual = next_page_resp.json()

        assert len(actual['articles']) == 5

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

    def test_update_article(self, drf_auth_client):
        profile = ProfileFactory(user__username='foo')
        articles = ArticleFactory.create_batch(size=5, author=profile)
        first = articles[0]

        url = reverse('articles:article-detail', args=(first.slug,))

        data = {
            'article': {
                "description": "foo's description"
            }
        }

        resp = drf_auth_client.put(url, json.dumps(data), content_type="application/json")

        actual = resp.json()['article']

        assert actual['description'] == "foo's description"

    def test_list_articles_by_author(self, drf_client):
        user_foo = UserFactory(username='foo')
        ArticleFactory.create_batch(size=5, author=user_foo.profile)

        url = reverse('articles:article-list') + '?' + urlencode({'author': user_foo.username})
        resp = drf_client.get(url)
        actual = resp.json()

        # it should equal foo's articles number
        assert actual['articlesCount'] == 5

        for article in actual['articles']:
            assert article['author']['username'] == user_foo.username

    def test_list_articles_favorited_by_username(self, drf_client):
        user_foo = UserFactory(username='foo')
        user_bar = UserFactory(username='bar')

        articles = ArticleFactory.create_batch(size=10, author=user_foo.profile)

        # user bar favorite the first 5 articles
        for article in articles[:5]:
            user_bar.profile.favorite(article)

        url = reverse('articles:article-list') + '?' + urlencode({'favorited': user_bar.username})
        resp = drf_client.get(url)
        actual = resp.json()

        # it should equal foo's articles number
        assert actual['articlesCount'] == 5

        for article in actual['articles']:
            assert article['author']['username'] == user_foo.username

    def test_list_articles_by_tag(self, drf_client):
        first_tag = TagFactory.create()
        second_tag = TagFactory.create()

        user_foo = UserFactory(username='foo')
        # articles with first tag
        ArticleFactory.create_batch(size=3, author=user_foo.profile, tags=(first_tag,))
        # articles with second tag
        ArticleFactory.create_batch(size=5, author=user_foo.profile, tags=(second_tag,))

        url = reverse('articles:article-list') + '?' + urlencode({'tag': first_tag.tag})
        resp = drf_client.get(url)
        actual = resp.json()

        assert actual['articlesCount'] == 3
        for article in actual['articles']:
            assert first_tag.tag in article['tagList']


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


class TestArticleFavoriteViews(object):

    def test_favorite_article(self, drf_auth_client):
        user = UserFactory.create(username="foo")
        article = ArticleFactory.create(author=user.profile, title='my article')

        url = reverse('articles:article-favorite', args=(article.slug,))

        resp = drf_auth_client.post(url)
        article = resp.json()['article']

        assert article['favorited']
        assert article['favoritesCount'] == 1

    def test_unfavorite_article(self, drf_auth_client):
        user = UserFactory.create(username="foo")
        article = ArticleFactory.create(author=user.profile, title='my article')

        drf_auth_client.user.profile.favorite(article)
        assert drf_auth_client.user.profile.has_favorited(article)

        url = reverse('articles:article-favorite', args=(article.slug,))
        resp = drf_auth_client.delete(url)

        assert resp.status_code == 204
        assert not drf_auth_client.user.profile.has_favorited(article)


class TestTagsListView(object):

    def test_list_tags(self, drf_client):
        # Overwrite faker sentence punctuation in this test
        from faker.providers.lorem import Provider
        Provider.sentence_punctuation = ''

        tags = TagFactory.create_batch(size=5)
        url = reverse('articles:tag-list')

        resp = drf_client.get(url)
        print(resp.json())
        actual = resp.json()['tags']

        actual_tags = sorted(actual)
        expected_tags = sorted([t.tag for t in tags])

        assert actual_tags == expected_tags


class TestArticleFeedViews(object):

    def test_feed_articles(self, drf_auth_client):
        user_foo = UserFactory.create(username="foo")
        user_bar = UserFactory.create(username="bar")

        ArticleFactory.create_batch(size=5, author=user_foo.profile)
        ArticleFactory.create_batch(size=10, author=user_bar.profile)

        # follow user `foo`
        drf_auth_client.user.profile.follow(user_foo.profile)

        url = reverse('articles:articles-feed')
        resp = drf_auth_client.get(url)
        actual = resp.json()

        # it should equal foo's articles number
        assert actual['articlesCount'] == 5

        for article in actual['articles']:
            assert article['author']['username'] == user_foo.username
