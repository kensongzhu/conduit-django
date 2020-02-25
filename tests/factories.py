import factory
from django.db.models.signals import post_save

from conduit.apps.articles.models import Article, Comment
from conduit.apps.authentication.models import User
from conduit.apps.profiles.models import Profile


def _post_generate_m2m(attr, create, extracted, **kwargs):
    if not create:
        # simple build, do nothing
        return

    if extracted:
        for instance in extracted:
            attr.add(instance)


@factory.django.mute_signals(post_save)
class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('first_name')
    email = factory.LazyAttribute(lambda obj: "%s@example.org" % obj.username.lower())
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')
    # then we pass 'user' to link the generated profile to our just generated User
    profile = factory.RelatedFactory('tests.factories.ProfileFactory', 'user')

    is_active = True
    is_staff = False
    is_superuser = False


@factory.django.mute_signals(post_save)
class ProfileFactory(factory.DjangoModelFactory):
    class Meta:
        model = Profile

    bio = factory.Faker('text', max_nb_chars=200, ext_word_list=None)
    image = factory.Faker('image_url', width=None, height=None)

    # pass profile as `None` to prevent UserFactory creating another profile
    # this disables the RelatedFactory
    user = factory.SubFactory(UserFactory, profile=None)

    @factory.post_generation
    def follows(self, create, extracted, **kwargs):
        _post_generate_m2m(self.follows, create, extracted, **kwargs)

    @factory.post_generation
    def favorites(self, create, extracted, **kwargs):
        _post_generate_m2m(self.favorites, create, extracted, **kwargs)


class ArticleFactory(factory.DjangoModelFactory):
    class Meta:
        model = Article

    slug = factory.Faker('slug')
    title = factory.Faker('sentence', nb_words=10, variable_nb_words=True, ext_word_list=None)

    description = factory.Faker('text', max_nb_chars=200, ext_word_list=None)
    body = factory.Faker('text', max_nb_chars=1000, ext_word_list=None)

    author = factory.SubFactory(ProfileFactory)


class CommentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Comment

    body = factory.Faker('text', max_nb_chars=144, ext_word_list=None)

    article = factory.SubFactory(ArticleFactory)
    author = factory.SubFactory(ProfileFactory)
