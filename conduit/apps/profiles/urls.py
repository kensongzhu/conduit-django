from django.urls import path

from .views import ProfileRetrieveAPIView, ProfileFollowAPIView

app_name = 'profiles'

urlpatterns = [
    path('profiles/<str:username>', ProfileRetrieveAPIView.as_view(), name='profile-detail'),
    path('profiles/<str:username>/follow', ProfileFollowAPIView.as_view(), name='profile-follow')
]
