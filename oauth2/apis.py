from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from .serializers import GetEtsyOauth2UrlSerializer


class EtsyOauth2API(ViewSet):

    @action(detail=False, methods=['post'], url_path='auth_url', url_name='auth-url')
    def get_auth_url(self, request):
        serializer = GetEtsyOauth2UrlSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        scopes = serializer.validated_data['scopes']
        etsy_api_key = settings.ETSY_API_KEY
        redirect_uri = f'{settings.BASE_URL}/oauth2/callback/'
        oauth2_url = f'https://www.etsy.com/oauth/connect?response_type=code&' \
                     f'client_id={etsy_api_key}&' \
                     f'redirect_uri={redirect_uri}&' \
                     f'scope={" ".join(scopes)}'

        return Response(oauth2_url, status=status.HTTP_200_OK)
