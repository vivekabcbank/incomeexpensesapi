from rest_framework import serializers
from .models import *


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ("date", "description", "amount","source")
