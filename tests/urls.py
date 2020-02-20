from django.urls import path, include

urlpatterns = [
    path('', include('conduit.urls'))
]
