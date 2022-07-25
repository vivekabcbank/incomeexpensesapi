from django.urls import path
from .views import *

urlpatterns = [
    path("",IncomeListAPIView.as_view(),name="incomes"),
    path("<int:id>",IncomeDetailsAPIView.as_view(),name="income"),
]