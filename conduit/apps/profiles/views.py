from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .renderers import ProfileJSONRenderer
from .serializers import ProfileSerializer


class ProfileRetrieveAPIView(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (AllowAny,)
    renderer_classes = (ProfileJSONRenderer,)
    queryset = Profile.objects.select_related('user')

    def retrieve(self, request, *args, **kwargs):
        username = kwargs.get('username', '')

        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound('The requested profile does not exist')

        serializer = self.serializer_class(profile, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileFollowAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def delete(self, request, **kwargs):
        follower = request.user.profile

        try:
            followee = Profile.objects.get(user__username=kwargs.get('username'))
        except Profile.DoesNotExist:
            raise NotFound('A profile with this username was not found.')

        follower.unfollow(followee)

        serializer = self.serializer_class(followee, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        follower = request.user.profile

        try:
            followee = Profile.objects.get(user__username=kwargs.get('username'))
        except Profile.DoesNotExist:
            raise NotFound('A profile with this username was not found.')

        if follower.pk is followee.pk:
            raise serializers.ValidationError("You can't follow yourself.")

        follower.follow(followee)

        serializer = self.serializer_class(followee, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_201_CREATED)
