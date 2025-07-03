from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from .models import User
from .serializers import UserSerializer, UserUpdateSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_statistics(request):
    """Returns user statistics and activity summary"""
    from core.models import Account, Asset
    from transactions.models import Transaction
    
    user = request.user
    now = datetime.now()
    
    # Statistiques des comptes
    accounts_stats = {
        'total_accounts': Account.objects.filter(user=user, is_active=True).count(),
        'total_balance': Account.objects.filter(user=user, is_active=True).aggregate(
            total=Sum('balance')
        )['total'] or 0
    }
    
    # Statistiques des assets
    assets_stats = {
        'total_assets': Asset.objects.filter(user=user, is_active=True).count(),
        'total_value': Asset.objects.filter(user=user, is_active=True).aggregate(
            total=Sum('current_value')
        )['total'] or 0
    }
    
    # Statistiques des transactions
    transactions_stats = {
        'total_transactions': Transaction.objects.filter(user=user).count(),
        'this_month_transactions': Transaction.objects.filter(
            user=user,
            date__gte=now.replace(day=1)
        ).count(),
        'first_transaction_date': Transaction.objects.filter(user=user).order_by('date').first().date if Transaction.objects.filter(user=user).exists() else None
    }
    
    # Calculs d'activité
    member_since_days = (now.date() - user.date_joined.date()).days
    avg_transactions_per_month = (transactions_stats['total_transactions'] / max(member_since_days / 30, 1)) if member_since_days > 0 else 0
    
    return Response({
        'user_info': {
            'member_since': user.date_joined,
            'member_since_days': member_since_days,
            'is_premium': user.is_premium
        },
        'accounts': accounts_stats,
        'assets': assets_stats,
        'transactions': transactions_stats,
        'activity': {
            'avg_transactions_per_month': round(avg_transactions_per_month, 1),
            'wealth_total': float(accounts_stats['total_balance'] + assets_stats['total_value'])
        }
    })
