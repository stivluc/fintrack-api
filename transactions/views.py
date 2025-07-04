from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, Avg, Max, Min
from django.db.models.functions import TruncMonth, TruncDate
from datetime import datetime, timedelta
from calendar import monthrange
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
        from core.models import Asset, Account
        
        user = request.user
        now = datetime.now()
        
        # Get date range from request, default to last 6 months
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = now - timedelta(days=180) # Default to 6 months ago

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = now

        # Ensure start_date is before end_date
        if start_date > end_date:
            start_date = end_date - timedelta(days=180)

        # Stats des 30 derniers jours
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)
        
        queryset = Transaction.objects.filter(user=user)
        
        current_month_transactions = queryset.filter(date__gte=thirty_days_ago.date())
        previous_month_transactions = queryset.filter(
            date__gte=sixty_days_ago.date(), 
            date__lt=thirty_days_ago.date()
        )
        
        current_income = current_month_transactions.filter(category__type='INCOME').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        current_expenses = current_month_transactions.filter(category__type='EXPENSE').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        previous_income = previous_month_transactions.filter(category__type='INCOME').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        previous_expenses = previous_month_transactions.filter(category__type='EXPENSE').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Calcul des variations
        income_change = ((current_income - previous_income) / previous_income * 100) if previous_income > 0 else 0
        expenses_change = ((abs(current_expenses) - abs(previous_expenses)) / abs(previous_expenses) * 100) if previous_expenses != 0 else 0
        
        # Patrimoine total (assets + comptes)
        total_assets = Asset.objects.filter(user=user, is_active=True).aggregate(
            total=Sum('current_value')
        )['total'] or 0
        
        total_accounts = Account.objects.filter(user=user, is_active=True).aggregate(
            total=Sum('balance')
        )['total'] or 0
        
        total_wealth = total_assets + total_accounts
        
        # Épargne ce mois (revenus - dépenses)
        current_savings = current_income + current_expenses  # expenses are negative
        previous_savings = previous_income + previous_expenses
        savings_change = ((current_savings - previous_savings) / abs(previous_savings) * 100) if previous_savings != 0 else 0
        
        # Évolution du patrimoine sur la période demandée
        wealth_evolution = []
        current_date = start_date
        
        while current_date <= end_date:
            # Calculate wealth for the current date
            # This is a simplified simulation. In a real app, you'd track historical asset values and account balances.
            # For demo purposes, we'll simulate fluctuations around the current total_wealth.
            
            # Get transactions up to this date
            transactions_up_to_date = queryset.filter(date__lte=current_date.date())
            
            # Calculate income and expenses up to this date
            income_up_to_date = transactions_up_to_date.filter(category__type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
            expenses_up_to_date = transactions_up_to_date.filter(category__type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
            
            # Simulate asset value changes over time
            # This is a placeholder for more complex asset tracking
            simulated_asset_value = float(total_assets) * (1 + (current_date - start_date).days / 365.0 * 0.05) # 5% annual growth
            
            # Simulate account balance changes based on income/expenses
            simulated_account_balance = float(total_accounts) + float(income_up_to_date) + float(expenses_up_to_date)

            # Add some random fluctuation for realism
            fluctuation = (random.random() - 0.5) * 0.05 * (simulated_asset_value + simulated_account_balance) # +/- 2.5% fluctuation
            
            daily_wealth = simulated_asset_value + simulated_account_balance + fluctuation

            wealth_evolution.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'wealth': round(daily_wealth, 2)
            })
            current_date += timedelta(days=1) # Increment by day for more granular data
        
        # Composition du patrimoine
        assets = Asset.objects.filter(user=user, is_active=True)
        composition = []
        
        # Grouper par type d'asset
        asset_composition = {}
        for asset in assets:
            asset_type = asset.get_asset_type_display()
            if asset_type not in asset_composition:
                asset_composition[asset_type] = 0
            asset_composition[asset_type] += float(asset.current_value)
        
        # Ajouter les comptes comme "Liquidités"
        if total_accounts > 0:
            asset_composition['Liquidités'] = float(total_accounts)
        
        # Convertir en format pour le frontend
        for name, value in asset_composition.items():
            composition.append({
                'name': name,
                'size': value,
                'index': len(composition)
            })
        
        return Response({
            'current_month': {
                'total_wealth': float(total_wealth),
                'wealth_change': 4.8,  # Simulation - à remplacer par un calcul réel
                'income': float(current_income),
                'income_change': float(income_change),
                'expenses': float(abs(current_expenses)),
                'expenses_change': float(expenses_change),
                'savings': float(current_savings),
                'savings_change': float(savings_change),
                'transactions_count': current_month_transactions.count()
            },
            'wealth_evolution': wealth_evolution,
            'wealth_composition': composition
        })
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Returns comprehensive analytics data for charts and insights"""
        user = request.user
        now = datetime.now()
        
        # Get period parameter (default to 6 months)
        period_months = int(request.query_params.get('months', 6))
        start_date = now - timedelta(days=period_months * 30)
        
        queryset = Transaction.objects.filter(user=user, date__gte=start_date)
        
        # 1. Monthly income vs expenses
        monthly_data = []
        for i in range(period_months):
            month_start = datetime(now.year, now.month, 1) - timedelta(days=i*30)
            month_start = month_start.replace(day=1)
            month_end = datetime(month_start.year, month_start.month, monthrange(month_start.year, month_start.month)[1])
            
            month_transactions = queryset.filter(date__gte=month_start, date__lte=month_end)
            
            income = month_transactions.filter(category__type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
            expenses = month_transactions.filter(category__type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_data.append({
                'month': month_start.strftime('%b'),
                'income': float(income),
                'expenses': float(abs(expenses))
            })
        
        monthly_data.reverse()  # Chronological order
        
        # 2. Category trends
        category_trends = []
        categories = queryset.filter(category__type='EXPENSE').values('category__name').distinct()
        
        for category in categories:
            category_name = category['category__name']
            monthly_amounts = []
            
            for i in range(period_months):
                month_start = datetime(now.year, now.month, 1) - timedelta(days=i*30)
                month_start = month_start.replace(day=1)
                month_end = datetime(month_start.year, month_start.month, monthrange(month_start.year, month_start.month)[1])
                
                amount = queryset.filter(
                    category__name=category_name,
                    date__gte=month_start,
                    date__lte=month_end
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                monthly_amounts.append({
                    'month': month_start.strftime('%b'),
                    'amount': float(abs(amount))
                })
            
            monthly_amounts.reverse()
            category_trends.append({
                'category': category_name,
                'data': monthly_amounts
            })
        
        # 3. Financial insights
        total_income = queryset.filter(category__type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = queryset.filter(category__type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
        
        savings = total_income + total_expenses  # expenses are negative
        avg_monthly_savings = savings / period_months if period_months > 0 else 0
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0
        
        # Biggest expense
        biggest_expense = queryset.filter(category__type='EXPENSE').order_by('amount').first()
        biggest_expense_data = None
        if biggest_expense:
            biggest_expense_data = {
                'amount': float(abs(biggest_expense.amount)),
                'description': biggest_expense.description,
                'category': biggest_expense.category.name,
                'date': biggest_expense.date.strftime('%Y-%m-%d')
            }
        
        return Response({
            'monthly_data': monthly_data,
            'category_trends': category_trends,
            'insights': {
                'avg_monthly_savings': float(avg_monthly_savings),
                'savings_rate': float(savings_rate),
                'biggest_expense': biggest_expense_data,
                'total_income': float(total_income),
                'total_expenses': float(abs(total_expenses)),
                'period_months': period_months
            }
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
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Returns budget overview with spending analysis"""
        user = request.user
        now = datetime.now()
        current_month_start = now.replace(day=1)
        
        budgets = self.get_queryset().filter(is_active=True)
        budget_overview = []
        
        total_allocated = 0
        total_spent = 0
        over_budget_count = 0
        
        for budget in budgets:
            # Calculer les dépenses du mois courant pour cette catégorie
            spent = Transaction.objects.filter(
                user=user,
                category=budget.category,
                date__gte=current_month_start
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            spent_abs = abs(spent)
            limit = budget.monthly_limit
            percentage = (spent_abs / limit * 100) if limit > 0 else 0
            remaining = limit - spent_abs
            
            # Status
            if percentage > 100:
                status = 'exceeded'
                over_budget_count += 1
            elif percentage > 80:
                status = 'warning'
            else:
                status = 'good'
            
            budget_overview.append({
                'id': budget.id,
                'category': {
                    'id': budget.category.id,
                    'name': budget.category.name,
                    'color': budget.category.color,
                    'icon': budget.category.icon
                },
                'allocated': float(limit),
                'spent': spent_abs,
                'remaining': float(remaining),
                'percentage': round(percentage, 1),
                'status': status,
                'days_left': (datetime(now.year, now.month + 1, 1) - now).days if now.month < 12 else (datetime(now.year + 1, 1, 1) - now).days
            })
            
            total_allocated += limit
            total_spent += spent_abs
        
        # Stats globales
        total_remaining = total_allocated - total_spent
        overall_percentage = (total_spent / total_allocated * 100) if total_allocated > 0 else 0
        
        # Données pour le graphique des dépenses
        expense_data = []
        for budget_item in budget_overview:
            if budget_item['spent'] > 0:
                expense_data.append({
                    'name': budget_item['category']['name'],
                    'value': budget_item['spent'],
                    'color': budget_item['category']['color']
                })
        
        return Response({
            'summary': {
                'total_allocated': float(total_allocated),
                'total_spent': float(total_spent),
                'total_remaining': float(total_remaining),
                'overall_percentage': round(overall_percentage, 1),
                'over_budget_count': over_budget_count,
                'budget_count': budgets.count()
            },
            'budgets': budget_overview,
            'expense_chart_data': expense_data
        })