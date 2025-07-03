from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from .models import Transaction, Budget
from .serializers import TransactionSerializer, BudgetSerializer


class TransactionFilter(DjangoFilterBackend):
    class Meta:
        model = Transaction
        fields = {
            'category': ['exact'],
            'account': ['exact'],
            'date': ['gte', 'lte', 'year', 'month'],
            'amount': ['gte', 'lte'],
            'is_recurring': ['exact'],
        }


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'account', 'is_recurring']
    search_fields = ['description']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        user = request.user
        now = datetime.now()
        current_month_start = now.replace(day=1)
        
        queryset = Transaction.objects.filter(user=user)
        
        # Stats du mois courant
        current_month_transactions = queryset.filter(date__gte=current_month_start)
        
        income = current_month_transactions.filter(category__type='INCOME').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        expenses = current_month_transactions.filter(category__type='EXPENSE').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Évolution des 6 derniers mois
        six_months_ago = now - timedelta(days=180)
        monthly_stats = queryset.filter(date__gte=six_months_ago).annotate(
            month=TruncMonth('date')
        ).values('month', 'category__type').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('month')
        
        return Response({
            'current_month': {
                'income': income,
                'expenses': abs(expenses),
                'balance': income + expenses,
                'transactions_count': current_month_transactions.count()
            },
            'monthly_evolution': monthly_stats
        })


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category', 'period', 'is_active']
    ordering_fields = ['monthly_limit', 'created_at']
    ordering = ['category__name']
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        user = request.user
        now = datetime.now()
        current_month_start = now.replace(day=1)
        
        budgets = self.get_queryset().filter(is_active=True)
        alerts = []
        
        for budget in budgets:
            spent = Transaction.objects.filter(
                user=user,
                category=budget.category,
                date__gte=current_month_start
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            spent_abs = abs(spent)
            limit = budget.monthly_limit
            percentage = (spent_abs / limit * 100) if limit > 0 else 0
            
            if percentage >= 80:
                alerts.append({
                    'budget_id': budget.id,
                    'category': budget.category.name,
                    'spent': spent_abs,
                    'limit': limit,
                    'percentage': round(percentage, 1),
                    'status': 'exceeded' if percentage > 100 else 'warning'
                })
        
        return Response({'alerts': alerts})
