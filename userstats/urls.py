from django.urls import path
from .views import *

urlpatterns = [
    path("expense_category_data",ExpenseSummaryStats.as_view(),name="expense-category-summary"),
    path("income_sources_data",IncomeSourcesSummaryStats.as_view(),name="income-sources-summary"),
]