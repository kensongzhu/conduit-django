import pytest

from ..factories import ProfileFactory, ArticleFactory


@pytest.mark.django_db
class TestProfileModel(object):

    def test_follow_and_unfollow_self(self):
        foo = ProfileFactory.create(user__username='foo')

        # follow self (follows won't change)
        foo.follow(foo)
        assert not foo.is_following(foo)
        assert not foo.is_followed_by(foo)

        # unfollow self
        foo.unfollow(foo)
        assert not foo.is_following(foo)
        assert not foo.is_followed_by(foo)

    def test_follow_and_unfollow_others(self):
        foo = ProfileFactory.create(user__username='foo')
        bar = ProfileFactory.create(user__username='bar')

        # one-way follow
        foo.follow(bar)
        assert foo.is_following(bar)
        assert not foo.is_followed_by(bar)

        foo.unfollow(bar)
        assert not foo.is_following(bar)
        assert not foo.is_followed_by(bar)

    def test_favorite_article(self):
        foo = ProfileFactory.create(user__username='foo')
        article_by_foo = ArticleFactory.create(author=foo)

        bar = ProfileFactory.create(user__username='bar')

        # bar favorite foo's article
        bar.favorite(article_by_foo)

        # assert if bar has already favorite foo's article
        assert bar.has_favorited(article_by_foo)

    def test_unfavorite_article(self):
        foo = ProfileFactory.create(user__username='foo')
        article_by_foo = ArticleFactory.create(author=foo)

        bar = ProfileFactory.create(user__username='bar', favorites=(article_by_foo,))

        bar.unfavorite(article_by_foo)

        # assert if bar does not favorite foo's article
        assert not bar.has_favorited(article_by_foo)
