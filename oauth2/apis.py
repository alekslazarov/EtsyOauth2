import requests
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy
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
                     f'scope={" ".join(scopes)}&' \
                     f'code_challenge={settings.ETSY_PKCE}'

        return Response(oauth2_url, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='callback', url_name='callback')
    def oauth2_callback(self, request):
        code = request.query_params.get('code')
        url = 'https://api.etsy.com/v3/public/oauth/token'
        payload = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': settings.ETSY_API_KEY,
            'redirect_uri': f'{settings.BASE_URL}/oauth2/callback/',
            'code_verifier': settings.ETSY_PKCE,
        }
        resp = requests.post(url, data=payload)
        if resp.status_code == 200:
            resp = resp.json()
            access_token = resp['access_token']
            refresh_token = resp['refresh_token']
            request.session['access_token'] = access_token
            request.session['refresh_token'] = refresh_token
            request.session['error'] = ''
        else:
            try:
                error_description = resp.json()["error_description"]
            except:
                error_description = 'Unknown Error'
            error = f'Failed to get Etsy tokens. Status code {resp.status_code}. Description: {error_description}. One time code was {code}'
            request.session['access_token'] = ''
            request.session['refresh_token'] = ''
            request.session['error'] = error

        return redirect(
            reverse_lazy('oauth2-view')
        )
