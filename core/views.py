from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from .models import Category, Account
from .serializers import CategorySerializer, AccountSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['type', 'is_default']
    search_fields = ['name']
    
    def get_queryset(self):
        user = self.request.user
        return Category.objects.filter(
            models.Q(user=user) | models.Q(user__isnull=True, is_default=True)
        ).distinct()


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'balance', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
