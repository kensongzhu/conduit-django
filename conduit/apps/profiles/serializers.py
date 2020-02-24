from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False)
    # image = serializers.SerializerMethodField()
    image = serializers.URLField(default='https://static.productionready.io/images/smiley-cyrus.jpg')
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'bio', 'image', 'following')
        read_only_fields = ('username',)

    def get_following(self, instance):
        request = self.context.get('request', None)

        if not request:
            return False

        if not request.user.is_authenticated:
            return False

        follower = request.user.profile
        followee = instance

        return follower.is_following(followee)

    # def get_image(self, obj):
    #     if obj.image:
    #         return obj.image
    #
    #     return 'https://static.productionready.io/images/smiley-cyrus.jpg'
