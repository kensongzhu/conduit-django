from django.db import models

from conduit.apps.authentication.models import User
from conduit.apps.core.models import TimestampedModel


class Profile(TimestampedModel):
    # There is an inherent relationship between the Profile and
    # User models. By creating a one-to-one relationship between the two,
    # we are formalizing this relationship. Every user will have on and only
    # one related Profile model.
    user = models.OneToOneField(
        User, on_delete=models.CASCADE
    )

    # Each user profile will have a field where they can tell other users
    # something about themselves. This field will be empty when the user
    # creates their account. so we specify blank = True
    bio = models.TextField(blank=True)

    # In addition to `bio` field, each user may have a profile image or avatar
    # This is not required and it may be blank.
    image = models.URLField(blank=True)

    # This is an example of a Many To Many relationship where both sides
    # of the relationship are of the same model. In this case, the model `Profile`
    # As mentioned in the text, this relationship will be one-way. Just because you are
    # following me does not mean that I am following you. This is
    # what `symmetrical=False` does for us.
    follows = models.ManyToManyField(
        'self',
        related_name='followed_by',
        symmetrical=False
    )

    def __str__(self):
        return self.user.username

    def follow(self, profile):
        """
        Follow `profile` if we'are not already following `profile`.

        :param profile:
        :return:
        """
        # you don't follow yourself
        if profile.pk != self.pk:
            self.follows.add(profile)

    def unfollow(self, profile):
        """
        Unfollow `profile` if we'are already following `profile`.

        :param profile:
        :return:
        """
        if profile.pk != self.pk:
            self.follows.remove(profile)

    def is_following(self, profile):
        """
        Return True if we're following `Profile`; False otherwise.

        :param profile:
        :return:
        """
        return self.follows.filter(pk=profile.pk).exists()

    def is_followed_by(self, profile):
        """
        Return True if `profile` following us; False otherwise.
        
        :param profile:
        :return:
        """

        return self.followed_by.filter(pk=profile.pk).exists()
