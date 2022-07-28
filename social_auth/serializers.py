from rest_framework import serializers
from . import facebook
from .register import *

class FacebookSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        # import pdb
        # pdb.set_trace()
        user_data = facebook.Facebook.validate(auth_token)
        try:
            user_id = user_data['id']
            name = user_data['name']
            provider = 'facebook'
            return register_social_user(
                provider=provider,
                social_login_id=user_id,
                name=name
            )
        except Exception as identifier:
            raise serializers.ValidationError(
                'The token  is invalid or expired. Please login again.'
            )