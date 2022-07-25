from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import *
from django.shortcuts import render
from .models import Expences
from rest_framework import permissions
from .permissions import *


class ExpenseList(ListCreateAPIView):
    serializer_class = ExpensesSerializer
    querysets = Expences.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.querysets.filter(owner=self.request.user)


class ExpenseDetailsAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ExpensesSerializer
    querysets = Expences.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    lookup_field = "id"

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.querysets.filter(owner=self.request.user)
