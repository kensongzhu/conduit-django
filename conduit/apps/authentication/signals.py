from django.db.models.signals import post_save
from django.dispatch import receiver

from conduit.apps.profiles.models import Profile
from .models import User


@receiver(post_save, sender=User)
def create_related_profile(sender, **kwargs):
    instance = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    if instance and created:
        instance.profile = Profile.objects.create(user=instance)
