import pytest
from django.utils.text import slugify

from conduit.apps.articles.serializers import ArticleSerializer
from ..factories import UserFactory, ArticleFactory


@pytest.mark.django_db
class TestArticlesSerializers(object):

    def test_article_serializer_presentation(self):
        article = ArticleFactory.create(author=UserFactory.create().profile)
        serializer = ArticleSerializer()
        result = serializer.to_representation(article)

        fields = list(serializer.Meta.fields)

        for k, v in result.items():
            assert k in fields

    def test_article_serializer_create(self):
        user = UserFactory.create()
        data = {'title': 'my article'}
        serializer = ArticleSerializer(data={'title': 'my article'}, partial=True, context={'author': user.profile})
        assert serializer.is_valid()

        article = serializer.create(serializer.validated_data)

        assert slugify(data['title']) in article.slug
        assert data['title'] == article.title
