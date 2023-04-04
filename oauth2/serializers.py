import json
from rest_framework import serializers
from rest_framework.validators import ValidationError


class GetEtsyOauth2UrlSerializer(serializers.Serializer):
    scopes = serializers.ListSerializer(child=serializers.CharField())

    def validate_scopes(self, scopes):
        available_scopes = [
            'address_r',
            'address_w',
            'billing_r',
            'cart_r',
            'cart_w',
            'email_r',
            'favorites_r',
            'favorites_w',
            'feedback_r',
            'listings_d',
            'listings_r',
            'listings_w',
            'profile_r',
            'profile_w',
            'recommend_r',
            'recommend_w',
            'shops_r',
            'shops_w',
            'transactions_r',
            'transactions_w',
        ]
        for scope in scopes:
            if scope not in available_scopes:
                raise ValidationError(f'Invalid scope {scope}')

        return scopes


class RefreshEtsyTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class CallEtsyAPISerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=[
        'get',
        'post',
        'put',
        'delete',
    ])
    url = serializers.CharField()
    payload = serializers.CharField(allow_blank=True, default='')
    access_token = serializers.CharField()

    def validate_url(self, url):
        if not url.startswith('https://openapi.etsy.com/v3/'):
            raise ValidationError('Any Etsy v3 api url should start with "https://openapi.etsy.com/v3/"')
        return url

    def validate_payload(self, payload):
        if payload == '':
            return ''
        try:
            return json.loads(payload)
        except:
            raise ValidationError('Payload should be a valid json format.')
