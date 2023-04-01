from django.urls import path

from .views import Oauth2View

urlpatterns = [
    path('', Oauth2View.as_view(), name='oauth2-view'),
]
