from rest_framework import serializers

from conduit.apps.profiles.serializers import ProfileSerializer
from .models import Article, Comment, Tag
from .relations import TagRelatedField


class ArticleSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    description = serializers.CharField(required=True)
    slug = serializers.SlugField(read_only=True)

    # Django REST Framework makes it possible to create read-only field that
    # gets its value by calling a function. In this case, the client expects
    # `created_at` to be called `createdAt` and `updated_at` to be `updatedAt`
    # `serializers.SerializerMethodField` is a good way to avoid having the
    # requirements of the client leak into our API.
    createdAt = serializers.SerializerMethodField(method_name='get_created_at')
    updatedAt = serializers.SerializerMethodField(method_name='get_updated_at')

    tagList = TagRelatedField(many=True, required=False, source='tags')

    favorited = serializers.SerializerMethodField()
    favoritesCount = serializers.SerializerMethodField(method_name='get_favorites_count')

    class Meta:
        model = Article
        fields = (
            'author',
            'body',
            'description',
            'slug',
            'title',
            'tagList',
            'createdAt',
            'updatedAt',
            'favorited',
            'favoritesCount',
        )

    def create(self, validated_data):
        author = self.context.get('author', None)
        tags = validated_data.pop('tags', [])
        article = Article.objects.create(author=author, **validated_data)

        for tag in tags:
            article.tags.add(tag)

        return article

    def get_created_at(self, instance):
        return instance.created_at.isoformat()

    def get_updated_at(self, instance):
        return instance.updated_at.isoformat()

    def get_favorited(self, instance):
        """
        Return `True` if the user who makes request favorite the article, otherwise `False`.
        :param instance:
        :return:
        """
        request = self.context.get('request', None)

        if not request:
            return False

        if not request.user.is_authenticated:
            return False

        return request.user.profile.has_favorited(instance)

    def get_favorites_count(self, instance):
        return instance.favorited_by.count()


class CommentSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(required=False)

    createdAt = serializers.SerializerMethodField(method_name='get_created_at')
    updatedAt = serializers.SerializerMethodField(method_name='get_updated_at')

    class Meta:
        model = Comment
        fields = (
            'id',
            'author',
            'body',
            'createdAt',
            'updatedAt',
        )

    def create(self, validated_data):
        article = self.context.get('article', None)
        author = self.context.get('author', None)

        return Comment.objects.create(article=article, author=author, **validated_data)

    def get_created_at(self, instance):
        return instance.created_at.isoformat()

    def get_updated_at(self, instance):
        return instance.updated_at.isoformat()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('tag',)

    def to_representation(self, instance):
        return instance.tag
