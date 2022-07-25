from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import *
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from rest_framework import views
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data["email"])
        token = RefreshToken.for_user(user).access_token
        cuurrent_site = get_current_site(request).domain
        relativelLink = reverse("email-verify")
        absurl = "http://" + cuurrent_site + relativelLink + "?token=" + str(token)
        email_body = "Hi " + user.username + " Use link below to verify your email \n" + absurl
        data = {"email_body": email_body, "to_email": user.email, "email_subject": "Verify your email"}
        Utils.send_email(data)
        return Response(user_data, status=status.HTTP_200_OK)


class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter("token",in_=openapi.IN_QUERY,description="Description",type=openapi.TYPE_STRING)

    # @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY,algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({"email":"successfully activated"}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({"error": "activation linked expired"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({"error": "Invalid token "}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


