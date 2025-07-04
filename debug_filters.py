#!/usr/bin/env python3
"""
Script de debug pour tester les filtres de date côté API
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fintrack.settings.production')
django.setup()

from transactions.models import Transaction
from transactions.views import TransactionFilter
from django.db.models import Q

def test_filters():
    """Test les filtres de date directement"""
    
    User = get_user_model()
    demo_user = User.objects.filter(email='demo@fintrack.com').first()
    
    if not demo_user:
        print("❌ Demo user not found")
        return
    
    print("🔍 Testing date filters...")
    print("=" * 50)
    
    # Test 1: Toutes les transactions
    all_transactions = Transaction.objects.filter(user=demo_user)
    print(f"📊 Total transactions: {all_transactions.count()}")
    
    # Afficher quelques dates pour debug
    recent_transactions = all_transactions.order_by('-date')[:5]
    print("\n📅 Recent transactions dates:")
    for t in recent_transactions:
        print(f"  - {t.date}: {t.description} ({t.amount}€)")
    
    # Test 2: Filtrer par date
    print(f"\n🔍 Testing date_gte filter (>= 2025-06-01):")
    filtered_gte = all_transactions.filter(date__gte='2025-06-01')
    print(f"  Results: {filtered_gte.count()} transactions")
    
    print(f"\n🔍 Testing date_lte filter (<= 2025-06-30):")
    filtered_lte = all_transactions.filter(date__lte='2025-06-30')
    print(f"  Results: {filtered_lte.count()} transactions")
    
    print(f"\n🔍 Testing date range (2025-06-01 to 2025-06-30):")
    filtered_range = all_transactions.filter(date__gte='2025-06-01', date__lte='2025-06-30')
    print(f"  Results: {filtered_range.count()} transactions")
    
    if filtered_range.exists():
        print("  Sample transactions:")
        for t in filtered_range[:3]:
            print(f"    - {t.date}: {t.description} ({t.amount}€)")
    
    # Test 3: Vérifier la classe TransactionFilter
    print(f"\n🔧 Testing TransactionFilter class:")
    try:
        filter_class = TransactionFilter
        print(f"  Filter class: {filter_class}")
        print(f"  Filter Meta model: {filter_class.Meta.model}")
        print(f"  Filter Meta fields: {filter_class.Meta.fields}")
    except Exception as e:
        print(f"  ❌ Error with filter class: {e}")
    
    # Test 4: Simuler les paramètres de requête
    print(f"\n🌐 Testing simulated API request:")
    query_params = {
        'date_gte': '2025-06-01',
        'date_lte': '2025-06-30'
    }
    
    try:
        # Simuler ce que fait DjangoFilterBackend
        queryset = Transaction.objects.filter(user=demo_user)
        
        if 'date_gte' in query_params:
            queryset = queryset.filter(date__gte=query_params['date_gte'])
        if 'date_lte' in query_params:
            queryset = queryset.filter(date__lte=query_params['date_lte'])
        
        print(f"  Simulated API result: {queryset.count()} transactions")
        
    except Exception as e:
        print(f"  ❌ Error simulating API: {e}")

if __name__ == '__main__':
    test_filters()