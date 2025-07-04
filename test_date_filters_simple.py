#!/usr/bin/env python3
"""
Test simple des filtres de date après correction
"""

import os
import sys
import django
import requests

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fintrack.settings.production')
django.setup()

def test_date_filters():
    """Test les filtres de date via l'API"""
    
    # URL de base (ajuster selon votre configuration)
    base_url = "http://localhost:8000/api/transactions/"
    
    # Données de test
    test_cases = [
        {
            'name': 'Toutes les transactions',
            'params': {}
        },
        {
            'name': 'Transactions depuis le 1er juin 2025',
            'params': {'date_gte': '2025-06-01'}
        },
        {
            'name': 'Transactions jusqu\'au 30 juin 2025',
            'params': {'date_lte': '2025-06-30'}
        },
        {
            'name': 'Transactions de juin 2025',
            'params': {'date_gte': '2025-06-01', 'date_lte': '2025-06-30'}
        },
        {
            'name': 'Transactions de juillet 2025',
            'params': {'date_gte': '2025-07-01', 'date_lte': '2025-07-31'}
        }
    ]
    
    print("🧪 Test des filtres de date pour les transactions")
    print("=" * 50)
    
    # Vous devez avoir un token d'auth pour cette partie
    # Pour un test local, vous pouvez utiliser:
    # 1. Créer un superuser: python manage.py createsuperuser
    # 2. Obtenir un token via l'API ou Django admin
    
    print("📝 Tests manuels à effectuer:")
    print()
    
    for test_case in test_cases:
        print(f"🔍 {test_case['name']}:")
        
        # Construire l'URL avec les paramètres
        url = base_url
        if test_case['params']:
            params = '&'.join([f"{k}={v}" for k, v in test_case['params'].items()])
            url += f"?{params}"
        
        print(f"   URL: {url}")
        print(f"   Curl: curl -H 'Authorization: Token YOUR_TOKEN' '{url}'")
        print()
    
    print("🔧 Pour tester automatiquement:")
    print("1. Obtenir un token d'authentification")
    print("2. Remplacer YOUR_TOKEN dans les commandes curl")
    print("3. Vérifier que les résultats correspondent aux dates demandées")
    print()
    print("✅ Les filtres devraient maintenant fonctionner correctement!")

if __name__ == '__main__':
    test_date_filters()