from rest_framework import serializers
from .models import *
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import *


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ("email", "username", "password",)

    def validate(self, attrs):
        errors = {}
        username = attrs.get('username', "")

        if not username.isalnum():
            errors["username"] = "The username should be alphanumeric"
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555, )

    class Meta:
        model = User
        fields = ("token",)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=68, min_length=6, read_only=True)
    # tokens = serializers.CharField(max_length=68, min_length=6, read_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(email=obj["email"])

        return {
            "access": user.tokens()["access"],
            "refresh": user.tokens()["refresh"]
        }

    class Meta:
        model = User
        fields = ("email", "password", "username", "tokens",)

    def validate(self, attrs):
        email = attrs.get('email', "")
        password = attrs.get('password', "")
        user = auth.authenticate(email=email, password=password)
        # import pdb
        # pdb.set_trace()
        if not user:
            raise AuthenticationFailed("IInvalid credentials, try again")

        if not user.is_active:
            raise AuthenticationFailed("Account disabled required, contact admin")

        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified")

        return {
            "email": email,
            "username": user.username,
            "tokens": user.tokens()
        }

        return super().validate(attrs)


class RequestPasswordEmailResetSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)
    redirect_url = serializers.CharField(max_length=500,required=False)

    class Meta:
        fields = ("email",)


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, max_length=68, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ("password", "token", "uidb64",)

    def validate(self, attrs):
        errors = {}
        try:
            password = attrs.get('password', "")
            token = attrs.get('token', "")
            uidb64 = attrs.get('uidb64', "")
            # import pdb
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                errors["error"] = "The reset linked is invalid"
            user.set_password(password)
            # pdb.set_trace()
            user.save()
            return (user)
        except Exception as identifier:
            errors["error"] = "provided input is invalid"
        if errors:
            raise serializers.ValidationError(errors)
        return super(SetNewPasswordSerializer, self).validate(self, attrs)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        "bad_token": "Token is expired other invalid"
    }

    def validate(self, attrs):
        self.token = attrs["refresh"]

    def save(self, **kwargs):
        try:
            RefreshToken(set.token).blacklist()
        except TokenError:
            self.fail("bad_token")
