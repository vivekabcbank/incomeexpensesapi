from authentication.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
import random


def generate_username(name):
    username = "".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)


def register_social_user(provider, social_login_id, name, email=""):
    filter_user = User.objects.filter(social_login_id=social_login_id)
    if filter_user.exists():
        user = filter_user[0]
        if provider == user.auth_provider:
            return {
                'username': user.username,
                'email': user.email,
                'tokens': user.tokens()
            }
        else:
            raise AuthenticationFailed(
                detail='Please continue your login using ' + user.auth_provider)
    else:
        user = {
            'username': generate_username(name), 'email': email,
            'password': social_login_id}
        user = User.objects.create_user(**user)
        user.is_verified = True
        user.auth_provider = provider
        user.social_login_id = social_login_id
        user.save()
        new_user = authenticate(
            email=email, password=social_login_id)
        return {
            'email': new_user.email,
            'username': new_user.username,
            'tokens': new_user.tokens()
        }
