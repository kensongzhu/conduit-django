from django.urls import path

from . import views

app_name = 'authentication'
urlpatterns = [
    path('user', views.UserRetrieveUpdateAPIView.as_view(), name='user-detail'),
    path('users', views.RegistrationAPIView.as_view(), name='registration'),
    path('users/login', views.LoginAPIView.as_view(), name='login')
]
