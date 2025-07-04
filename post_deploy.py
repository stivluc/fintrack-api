#!/usr/bin/env python3
"""
Script de post-déploiement pour Render
Exécute les migrations et populate les données sur la vraie DB
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Post-deployment setup"""
    # S'assurer qu'on utilise les settings de production
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fintrack.settings.production')
    
    # Initialiser Django
    django.setup()
    
    print("🚀 Post-deployment setup starting...")
    
    try:
        # Exécuter les migrations sur la vraie DB
        print("📊 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
        # Nettoyer les données existantes pour éviter les duplicatas
        print("🧹 Cleaning existing demo data...")
        execute_from_command_line(['manage.py', 'shell', '-c', '''
from django.contrib.auth import get_user_model
from core.models import Account, Asset, Category
from transactions.models import Transaction, Budget
User = get_user_model()
demo_user = User.objects.filter(email="demo@fintrack.com").first()
if demo_user:
    Transaction.objects.filter(user=demo_user).delete()
    Budget.objects.filter(user=demo_user).delete()
    Asset.objects.filter(user=demo_user).delete()
    Account.objects.filter(user=demo_user).delete()
    print("✅ Demo data cleaned")
'''])
        
        # Populate les catégories
        print("📂 Populating categories...")
        execute_from_command_line(['manage.py', 'populate_categories'])
        
        # Populate les données de démo
        print("🎭 Populating demo data...")
        execute_from_command_line(['manage.py', 'populate_demo_data'])
        
        print("✅ Post-deployment setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during post-deployment: {e}")
        # Ne pas faire échouer le déploiement, juste logger
        print("⚠️ Some setup steps failed, but deployment continues...")

if __name__ == '__main__':
    main()