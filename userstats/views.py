from django.shortcuts import render
from rest_framework.views import APIView
import datetime
from expences.models import Expences
from rest_framework.response import Response
from rest_framework import status
from income.models import Income

class ExpenseSummaryStats(APIView):
    def get_amount_for_category(self,expense_list,category):
        expenses = expense_list.filter(category=category)
        amount = 0
        for expense in expenses:
            amount += expense.amount
        return {"amount":str(amount)}

    def get_categories(self,expense):
        return expense.category

    def get(self,request):
        todays_date = datetime.date.today()
        ayear_ago = todays_date-datetime.timedelta(30*12)
        # import pdb
        # pdb.set_trace()
        expenses = Expences.objects.filter(owner=request.user,date__gte=ayear_ago,date__lte=todays_date)

        final = {}
        categories = list(set(map(self.get_categories,expenses)))

        for expense in expenses:
            for category in categories:
                final[category] = self.get_amount_for_category(expenses,category)

        return Response({"category_data":final},status=status.HTTP_200_OK)


class IncomeSourcesSummaryStats(APIView):
    def get_amount_for_source(self,income_list,source):
        incomes = income_list.filter(source=source)
        amount = 0
        for income in incomes:
            amount += income.amount
        return {"amount":str(amount)}

    def get_sources(self,income):
        return income.source

    def get(self,request):
        todays_date = datetime.date.today()
        ayear_ago = todays_date-datetime.timedelta(30*12)
        incomes = Income.objects.filter(owner=request.user,date__gte=ayear_ago,date__lte=todays_date)

        final = {}
        sources = list(set(map(self.get_sources,incomes)))

        for i in incomes:
            for source in sources:
                final[source] = self.get_amount_for_source(incomes,source)

        return Response({"income_source_data":final},status=status.HTTP_200_OK)


'''
{
  "email": vivek.athilkar100@gmail.com",
  "password": "vivek@ATH10"
}
'''
