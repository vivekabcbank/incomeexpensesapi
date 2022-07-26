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
from .renderers import *

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import *

class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRender,)

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
    renderer_classes = (UserRender,)
    token_param_config = openapi.Parameter("token",in_=openapi.IN_QUERY,description="Description",type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
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
    renderer_classes = (UserRender,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(GenericAPIView):
    serializer_class = RequestPasswordEmailResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data.get('email', "")
        user = User.objects.filter(email=email)
        if user.exists():
            user = user.first()
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            cuurrent_site = get_current_site(request).domain
            relativelLink = reverse("password-reset-confirm", kwargs={"uidb64": uidb64, "token": token})
            absurl = "http://" + cuurrent_site + relativelLink
            email_body = "Hi Use link below to reset-confirm your password \n" + absurl
            data = {"email_body": email_body, "to_email": user.email, "email_subject": "Verify your email"}
            Utils.send_email(data)
        return Response({"success":"We have sent your a link to reset your password"},status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(GenericAPIView):

    def get(self, request,uidb64,token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                return Response({"error":"Token is not valid, please request a new one"},status=status.HTTP_401_UNAUTHORIZED)
            return Response({"success":True,"message":"credentials valid","uidb64":uidb64,"token":token},status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as identifier:
            return Response({"error": "Token is not valid, please request a new one"},status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordAPIView(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self,request):
        response = {}
        serializer = self.serializer_class(data=request.data)
        # serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            return Response({"status": True, "message": "Password reset success"}, status=status.HTTP_200_OK)
        else:
            response["errors"] = serializer.errors
            response["status"] = status.HTTP_401_UNAUTHORIZED
            response["errordata"] = {"status": False, "message": "Password reset failed"}
            return Response(response)
