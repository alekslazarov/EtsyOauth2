import logging
import random
import hashlib
import base64
import requests
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from .serializers import (
    GetEtsyOauth2UrlSerializer,
    RefreshEtsyTokenSerializer,
    CallEtsyAPISerializer,
)


class EtsyOauth2API(ViewSet):
    logger = logging.getLogger('etsy')

    @action(detail=False, methods=['post'], url_path='auth_url', url_name='auth-url')
    def get_auth_url(self, request):
        serializer = GetEtsyOauth2UrlSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        scopes = serializer.validated_data['scopes']
        etsy_api_key = settings.ETSY_API_KEY
        pkce = settings.ETSY_PKCE
        pkce_sha_256 = hashlib.sha256(pkce.encode('utf-8')).digest()
        pkce_b64 = base64.urlsafe_b64encode(pkce_sha_256)
        code_challenge = pkce_b64.decode('utf-8').replace('=', '')
        redirect_uri = f'{settings.BASE_URL}/oauth2/callback/'
        oauth2_url = f'https://www.etsy.com/oauth/connect?response_type=code&' \
                     f'client_id={etsy_api_key}&' \
                     f'redirect_uri={redirect_uri}&' \
                     f'scope={" ".join(scopes)}&' \
                     f'state={settings.ETSY_STATE}&' \
                     f'code_challenge={code_challenge}&' \
                     f'code_challenge_method=S256'

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
            error = f'Failed to get Etsy tokens. Status code {resp.status_code}. Description: {error_description}.'
            request.session['access_token'] = ''
            request.session['refresh_token'] = ''
            request.session['error'] = error

        return redirect(
            reverse_lazy('oauth2-view')
        )

    @action(detail=False, methods=['post'], url_path='refresh_token', url_name='refresh-token')
    def refresh_token(self, request):
        serializer = RefreshEtsyTokenSerializer(data=request.data)
        if not serializer.is_valid():
            errors_ary = [error for field, error in serializer.errors.items()]
            return Response({'error': errors_ary[0]}, status=status.HTTP_400_BAD_REQUEST)

        refresh_token = serializer.validated_data['refresh_token']
        url = 'https://api.etsy.com/v3/public/oauth/token'
        payload = {
            'grant_type': 'refresh_token',
            'client_id': settings.ETSY_API_KEY,
            'refresh_token': refresh_token
        }
        resp = requests.post(url, data=payload)

        if resp.status_code == 200:
            resp = resp.json()
            access_token = resp['access_token']
            refresh_token = resp['refresh_token']
            request.session['access_token'] = access_token
            request.session['refresh_token'] = refresh_token

            return Response({
                'access_token': access_token,
                'refresh_token': refresh_token
            })

        else:
            request.session['access_token'] = ''
            request.session['refresh_token'] = ''

            return Response(
                {'error': f'API call failed. Status code: {resp.status_code}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='call_api', url_name='call-api')
    def call_etsy_api(self, request):
        serializer = CallEtsyAPISerializer(data=request.data)
        if not serializer.is_valid():
            errors_ary = [error for field, error in serializer.errors.items()]
            return Response(
                {
                    'status_code': 'None',
                    'error': errors_ary[0]
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        method = serializer.validated_data['method']
        url = serializer.validated_data['url']
        payload = serializer.validated_data['payload']
        access_token = serializer.validated_data['access_token']

        # print log
        request_id = random.randint(100, 999)  # this is for logging
        request_log = f'---------- Etsy API Request. Id: {request_id} ----------\n' \
                      f'Method: {method}\n' \
                      f'Url: {url}\n' \
                      f'Payload: {payload}'
        self.logger.info(request_log)

        resp = requests.request(
            method=method,
            url=url,
            data=payload,
            headers={
                'x-api-key': settings.ETSY_API_KEY,
                'Authorization': f'Bearer {access_token}'
            }
        )
        if resp.status_code < 300:
            # print log
            response_log = f'---------- Etsy API Response. Id: {request_id} ----------\n' \
                           f'Status: Success\n' \
                           f'Code: {resp.status_code}'
            self.logger.info(response_log)
            try:
                res = {
                    'status_code': resp.status_code,
                    'result': resp.json()
                }
            except:
                res = {
                    'status_code': resp.status_code,
                    'result': None
                }
            return Response(res, status=status.HTTP_200_OK)

        else:
            try:
                error = resp.json()
                if 'error_description' in error:
                    error = error['error_description']
                elif 'error' in error:
                    error = error['error']
                else:
                    error = 'Unknown error'
            except Exception as e:
                self.logger.error('Unexpected error to get etsy api request error message. %s', e)
                error = 'Unknown error'

            res = {
                'status_code': resp.status_code,
                'error': error
            }

            # print log
            response_log = f'---------- Etsy API Response. Id: {request_id} ----------\n' \
                           f'Status: Fail\n' \
                           f'Code: {resp.status_code}\n' \
                           f'Error: {error}'
            self.logger.warning(response_log)

            return Response(res, status=status.HTTP_400_BAD_REQUEST)
