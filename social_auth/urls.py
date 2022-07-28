from django.urls import path
from .views import *

urlpatterns = [
    path('facebook/', FacebookSocialAuthView.as_view()),
]