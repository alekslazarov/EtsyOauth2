from django.urls import path, include
from rest_framework import routers

from .apis import EtsyOauth2API
from .views import Oauth2View

router = routers.SimpleRouter()
router.register('', EtsyOauth2API, basename='oauth2')

urlpatterns = [
    path('', Oauth2View.as_view(), name='oauth2-view'),
    path('oauth2/', include(router.urls))
]
