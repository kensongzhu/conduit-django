import json

import factory
import pytest
from django.shortcuts import reverse
from django.utils.text import slugify

from ..factories import ProfileFactory, ArticleFactory


@pytest.mark.django_db
def test_create_article(drf_client):
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
def test_list_articles(drf_client):
    ArticleFactory.create_batch(size=10, author=ProfileFactory(user__username='author1'))
    ArticleFactory.create_batch(size=5, author=ProfileFactory(user__username='author2'))

    url = reverse('articles:article-list')
    resp = drf_client.get(url)
    actual = resp.json()['articles']

    assert len(actual) == 15


@pytest.mark.django_db
def test_get_articles_by_slug(drf_client):
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
def test_update_article(drf_client):
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
