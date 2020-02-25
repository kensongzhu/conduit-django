from django.db import models

from conduit.apps.core.models import TimestampedModel


class Article(TimestampedModel):
    slug = models.SlugField(db_index=True, max_length=255, unique=True)
    title = models.CharField(db_index=True, max_length=255)

    description = models.TextField()
    body = models.TextField()

    # Every article must have an author. This will answer questions like "Who gets credit for
    # writing this article?" and "Who can edit this article?"
    # Unlike the `User` <-> `Profile` relationship, this is a simple foreign key (many-to-one)
    # relationship. In this case, one `Profile` can have many `Articles`s
    author = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='articles'
    )

    tags = models.ManyToManyField('articles.Tag', related_name='articles')

    def __str__(self):
        return self.title


class Comment(TimestampedModel):
    body = models.TextField()

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='comments'
    )

    author = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name="comments"
    )


class Tag(TimestampedModel):
    tag = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True, unique=True)

    def __str__(self):
        return self.tag
