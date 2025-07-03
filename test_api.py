#!/usr/bin/env python3
"""
Script pour tester l'API FinTrack
Usage: python test_api.py
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
DEMO_USER = {
    "email": "demo@fintrack.com",
    "password": "demo123"
}

def test_api():
    print("🧪 Test de l'API FinTrack")
    print("=" * 40)
    
    # 1. Test de connexion
    print("\n1. Test de connexion...")
    login_response = requests.post(f"{BASE_URL}/auth/jwt/create/", data=DEMO_USER)
    
    if login_response.status_code == 200:
        token = login_response.json()["access"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Connexion réussie")
    else:
        print("❌ Échec de connexion:", login_response.text)
        return
    
    # 2. Test des catégories
    print("\n2. Test des catégories...")
    categories = requests.get(f"{BASE_URL}/categories/", headers=headers)
    if categories.status_code == 200:
        print(f"✅ {len(categories.json()['results'])} catégories récupérées")
    else:
        print("❌ Erreur catégories:", categories.status_code)
    
    # 3. Test des comptes
    print("\n3. Test des comptes...")
    accounts = requests.get(f"{BASE_URL}/accounts/", headers=headers)
    if accounts.status_code == 200:
        print(f"✅ {len(accounts.json()['results'])} comptes récupérés")
    else:
        print("❌ Erreur comptes:", accounts.status_code)
    
    # 4. Test des transactions
    print("\n4. Test des transactions...")
    transactions = requests.get(f"{BASE_URL}/transactions/", headers=headers)
    if transactions.status_code == 200:
        print(f"✅ {len(transactions.json()['results'])} transactions récupérées")
    else:
        print("❌ Erreur transactions:", transactions.status_code)
    
    # 5. Test du dashboard
    print("\n5. Test du dashboard...")
    dashboard = requests.get(f"{BASE_URL}/transactions/dashboard_stats/", headers=headers)
    if dashboard.status_code == 200:
        stats = dashboard.json()
        print(f"✅ Stats dashboard: {stats['current_month']['income']}€ revenus, {stats['current_month']['expenses']}€ dépenses")
    else:
        print("❌ Erreur dashboard:", dashboard.status_code)
    
    # 6. Test des budgets
    print("\n6. Test des budgets...")
    budgets = requests.get(f"{BASE_URL}/budgets/", headers=headers)
    if budgets.status_code == 200:
        print(f"✅ {len(budgets.json()['results'])} budgets récupérés")
    else:
        print("❌ Erreur budgets:", budgets.status_code)
    
    print("\n" + "=" * 40)
    print("🎉 Tests terminés ! L'API est prête pour le déploiement.")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API. Vérifiez que le serveur Django est lancé avec:")
        print("python manage.py runserver")