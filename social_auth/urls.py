from django.urls import path
from .views import *

urlpatterns = [
    path('facebook/', FacebookSocialAuthView.as_view()),
    path('twitter/', TwitterSocialAuthView.as_view()),
    path('google/', GoogleSocialAuthView.as_view()),
]