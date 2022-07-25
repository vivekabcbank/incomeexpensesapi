from django.urls import path
from .views import *

urlpatterns = [
    path("",ExpenseList.as_view(),name="expenses"),
    path("<int:id>",ExpenseDetailsAPIView.as_view(),name="expense"),
]