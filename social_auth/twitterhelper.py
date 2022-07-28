import twitter
import os
from rest_framework import serializers
from django.conf import settings

class TwitterAuthTokenVerification:

    @staticmethod
    def validate_twitter_auth_tokens(access_token_key, access_token_secret):
        consumer_api_key = settings.TWITTER_API_KEY
        consumer_api_secret_key = settings.TWITTER_CONSUMER_SECRET
        try:
            api = twitter.Api(
                consumer_key=consumer_api_key,
                consumer_secret=consumer_api_secret_key,
                access_token_key=access_token_key,
                access_token_secret=access_token_secret
            )
            user_profile_info = api.VerifyCredentials(include_email=True)
            return user_profile_info.__dict__
        except Exception as identifier:

            raise serializers.ValidationError({
                "tokens": ["The tokens are invalid or expired"]})
