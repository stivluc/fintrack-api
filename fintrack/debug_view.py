from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from core.models import Category, CategoryType
from transactions.models import Transaction
from datetime import datetime, timedelta

User = get_user_model()

@csrf_exempt
def debug_dashboard(request):
    """Vue temporaire pour débugger les problèmes de dashboard"""
    try:
        # Récupérer l'utilisateur démo
        demo_user = User.objects.get(email='demo@fintrack.com')
        
        # Vérifier les catégories de revenus
        income_categories = Category.objects.filter(type=CategoryType.INCOME)
        expense_categories = Category.objects.filter(type=CategoryType.EXPENSE)
        
        # Vérifier les transactions des 30 derniers jours
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_transactions = Transaction.objects.filter(
            user=demo_user,
            date__gte=thirty_days_ago.date()
        )
        
        # Grouper par type
        income_transactions = recent_transactions.filter(category__type=CategoryType.INCOME)
        expense_transactions = recent_transactions.filter(category__type=CategoryType.EXPENSE)
        
        # Si pas de catégories de revenus, en créer
        if not income_categories.exists():
            # Créer quelques catégories de base
            salary_cat = Category.objects.create(
                name='Salaire',
                type=CategoryType.INCOME,
                color='#10B981',
                is_default=True
            )
            freelance_cat = Category.objects.create(
                name='Freelance',
                type=CategoryType.INCOME,
                color='#059669',
                is_default=True
            )
            other_cat = Category.objects.create(
                name='Autres revenus',
                type=CategoryType.INCOME,
                color='#047857',
                is_default=True
            )
            
            # Mettre à jour les transactions de revenus sans catégorie ou mal catégorisées
            positive_transactions = recent_transactions.filter(amount__gt=0)
            for trans in positive_transactions:
                if 'salaire' in trans.description.lower():
                    trans.category = salary_cat
                elif 'freelance' in trans.description.lower():
                    trans.category = freelance_cat
                else:
                    trans.category = other_cat
                trans.save()
        
        # Recalculer après corrections
        income_transactions = recent_transactions.filter(category__type=CategoryType.INCOME)
        expense_transactions = recent_transactions.filter(category__type=CategoryType.EXPENSE)
        
        total_income = sum(t.amount for t in income_transactions)
        total_expenses = sum(abs(t.amount) for t in expense_transactions)
        
        return JsonResponse({
            'debug_info': {
                'demo_user_id': demo_user.id,
                'income_categories_count': Category.objects.filter(type=CategoryType.INCOME).count(),
                'expense_categories_count': Category.objects.filter(type=CategoryType.EXPENSE).count(),
                'total_transactions_30_days': recent_transactions.count(),
                'income_transactions_count': income_transactions.count(),
                'expense_transactions_count': expense_transactions.count(),
                'total_income_calculated': float(total_income),
                'total_expenses_calculated': float(total_expenses),
            },
            'recent_transactions': [
                {
                    'date': t.date.isoformat(),
                    'description': t.description,
                    'amount': float(t.amount),
                    'category_name': t.category.name if t.category else 'No category',
                    'category_type': t.category.type if t.category else 'Unknown'
                }
                for t in recent_transactions.order_by('-date')[:20]
            ]
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)