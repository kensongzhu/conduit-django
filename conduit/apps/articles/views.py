from rest_framework import mixins, viewsets, status, generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article
from .models import Comment
from .models import Tag
from .renderers import ArticleJSONRenderer
from .renderers import CommentJSONRenderer
from .serializers import ArticleSerializer
from .serializers import CommentSerializer
from .serializers import TagSerializer


class ArticleViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (ArticleJSONRenderer,)
    queryset = Article.objects.select_related('author', 'author__user')
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = self.queryset
        # query params
        author = self.request.query_params.get('author', None)
        tag = self.request.query_params.get('tag', None)
        favorited_by = self.request.query_params.get('favorited', None)

        if author is not None:
            queryset = queryset.filter(author__user__username=author)

        if tag is not None:
            queryset = queryset.filter(tags__tag=tag)

        if favorited_by is not None:
            queryset = queryset.filter(favorited_by__user__username=favorited_by)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer_context = {
            'author': request.user.profile,
            'request': request
        }

        serializer_data = request.data.get('article', {})

        serializer = self.serializer_class(data=serializer_data, context=serializer_context)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        serializer_context = {'request': request}
        page_instances = self.paginate_queryset(self.get_queryset())

        serializer = self.serializer_class(
            instance=page_instances,
            context=serializer_context,
            many=True
        )

        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer_context = {'request': request}

        try:
            serializer_instance = self.queryset.get(slug=kwargs.get('slug', ''))
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        serializer = self.serializer_class(instance=serializer_instance, context=serializer_context)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_context = {'request': request}

        try:
            serializer_instance = self.queryset.get(slug=kwargs.get('slug', ''))
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        serializer_data = request.data.get('article', {})

        serializer = self.serializer_class(
            instance=serializer_instance,
            data=serializer_data,
            context=serializer_context,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ArticlesFavoriteAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer

    def post(self, request, **kwargs):
        profile = request.user.profile
        serializer_context = {'request': request}

        try:
            article = Article.objects.get(slug=kwargs.get('article_slug'))
        except Article.DoesNotExist:
            raise NotFound('An article with this slug was not found.')

        profile.favorite(article)

        serializer = self.serializer_class(
            instance=article,
            context=serializer_context
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        profile = request.user.profile
        serializer_context = {'request': request}

        try:
            article = Article.objects.get(slug=kwargs.get('article_slug'))
        except Article.DoesNotExist:
            raise NotFound('An article with this slug was not found.')

        profile.unfavorite(article)

        serializer = self.serializer_class(
            instance=article,
            context=serializer_context
        )

        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (CommentJSONRenderer,)
    queryset = Comment.objects.select_related(
        'author',
        'author__user',
        'article',
        'article__author',
        'article__author__user'
    )
    lookup_field = 'article__slug'
    lookup_url_kwarg = 'article_slug'

    def filter_queryset(self, queryset):
        # The built-in list function calls `filter_queryset`. Since we only
        # want comments for a specific article, this is a good place to do
        # that filtering.
        filters = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}

        return queryset.filter(**filters)

    def create(self, request, *args, **kwargs):
        data = request.data.get('comment', {})
        context = {'author': request.user.profile}

        try:
            context['article'] = Article.objects.get(slug=kwargs.get('article_slug'))
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDestroyAPIView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    lookup_field = 'comment_pk'
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def destroy(self, request, *args, **kwargs):
        try:
            comment = Comment.objects.get(pk=kwargs.get('comment_pk'))
        except Comment.DoesNotExist:
            raise NotFound('A comment with this ID does not exist.')

        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TagListAPIView(generics.ListAPIView):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        serializer_instances = self.get_queryset()
        serializer = self.serializer_class(instance=serializer_instances, many=True)

        return Response({'tags': serializer.data}, status=status.HTTP_200_OK)


class ArticlesFeedAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Article.objects.all()
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(
            author__in=self.request.user.profile.follows.all()
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        serializer_context = {'request': request}
        serializer = self.serializer_class(instance=page, context=serializer_context, many=True)

        return self.get_paginated_response(serializer.data)
