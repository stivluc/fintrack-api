#!/usr/bin/env python3
"""
Script de test pour vérifier que la population ne crée pas de duplicatas
Exécute la population plusieurs fois et vérifie les compteurs
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fintrack.settings.production')
django.setup()

from core.models import Category, Account, Asset
from transactions.models import Transaction, Budget

User = get_user_model()

def print_stats():
    """Affiche les statistiques de la base de données"""
    demo_user = User.objects.filter(email='demo@fintrack.com').first()
    if not demo_user:
        print("❌ Demo user not found")
        return
    
    stats = {
        'Users': User.objects.count(),
        'Categories': Category.objects.count(),
        'Accounts': Account.objects.filter(user=demo_user).count(),
        'Transactions': Transaction.objects.filter(user=demo_user).count(),
        'Budgets': Budget.objects.filter(user=demo_user).count(),
        'Assets': Asset.objects.filter(user=demo_user).count(),
    }
    
    print("\n📊 Database Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return stats

def main():
    """Test principal"""
    print("🧪 Testing population script for duplicates...")
    
    print("\n1️⃣ First populate run:")
    execute_from_command_line(['manage.py', 'populate_demo_data'])
    stats1 = print_stats()
    
    print("\n2️⃣ Second populate run (should not create duplicates):")
    execute_from_command_line(['manage.py', 'populate_demo_data'])
    stats2 = print_stats()
    
    print("\n3️⃣ Third populate run (should not create duplicates):")
    execute_from_command_line(['manage.py', 'populate_demo_data'])
    stats3 = print_stats()
    
    # Vérifier les duplicatas
    print("\n🔍 Checking for duplicates...")
    all_good = True
    
    # Les utilisateurs, catégories, comptes, budgets et assets ne doivent pas changer
    stable_fields = ['Users', 'Categories', 'Accounts', 'Budgets', 'Assets']
    for field in stable_fields:
        if stats1[field] != stats2[field] or stats2[field] != stats3[field]:
            print(f"❌ {field} changed between runs: {stats1[field]} -> {stats2[field]} -> {stats3[field]}")
            all_good = False
        else:
            print(f"✅ {field} stable: {stats1[field]}")
    
    # Les transactions peuvent changer légèrement car les random sont regénérées
    # Mais elles ne doivent pas exploser
    trans_diff_1_2 = abs(stats2['Transactions'] - stats1['Transactions'])
    trans_diff_2_3 = abs(stats3['Transactions'] - stats2['Transactions'])
    
    if trans_diff_1_2 > 110 or trans_diff_2_3 > 110:  # 100 transactions random + marge
        print(f"❌ Transactions changed too much: {stats1['Transactions']} -> {stats2['Transactions']} -> {stats3['Transactions']}")
        all_good = False
    else:
        print(f"✅ Transactions stable (small variation expected): {stats1['Transactions']} -> {stats2['Transactions']} -> {stats3['Transactions']}")
    
    if all_good:
        print("\n🎉 SUCCESS: No significant duplicates detected!")
        print("📝 The populate script can be safely run multiple times.")
    else:
        print("\n⚠️  WARNING: Potential duplicates detected!")
        print("🔧 The populate script may need further adjustments.")
    
    return all_good

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error during test: {e}")
        sys.exit(1)