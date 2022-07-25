from rest_framework import serializers
from .models import *


class ExpensesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expences
        fields = ("date", "description", "amount","category")
