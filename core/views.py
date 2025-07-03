from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from django.db.models import Sum
from .models import Category, Account, Asset
from .serializers import CategorySerializer, AccountSerializer, AssetSerializer


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


class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['asset_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'current_value', 'created_at']
    ordering = ['-current_value']
    
    def get_queryset(self):
        return Asset.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def portfolio_summary(self, request):
        """Returns portfolio summary with total value and composition"""
        user = request.user
        assets = Asset.objects.filter(user=user, is_active=True)
        
        total_value = assets.aggregate(total=Sum('current_value'))['total'] or 0
        
        # Group by asset type
        composition = {}
        for asset in assets:
            asset_type = asset.get_asset_type_display()
            if asset_type not in composition:
                composition[asset_type] = {
                    'name': asset_type,
                    'value': 0,
                    'count': 0
                }
            composition[asset_type]['value'] += float(asset.current_value)
            composition[asset_type]['count'] += 1
        
        # Add percentage
        for asset_type in composition:
            if total_value > 0:
                composition[asset_type]['percentage'] = (composition[asset_type]['value'] / float(total_value)) * 100
            else:
                composition[asset_type]['percentage'] = 0
        
        return Response({
            'total_value': total_value,
            'asset_count': assets.count(),
            'composition': list(composition.values())
        })
