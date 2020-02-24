import pytest

from ..factories import ProfileFactory


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
