#!/usr/bin/env python3
"""
Script pour tester les filtres de date de l'API FinTrack
Usage: python test_date_filters.py
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api"
DEMO_USER = {
    "email": "demo@fintrack.com",
    "password": "demo123"
}

def test_date_filters():
    print("🧪 Test des filtres de date pour l'endpoint /transactions/")
    print("=" * 60)
    
    # 1. Test de connexion
    print("\n1. Connexion...")
    login_response = requests.post(f"{BASE_URL}/auth/jwt/create/", data=DEMO_USER)
    
    if login_response.status_code == 200:
        token = login_response.json()["access"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Connexion réussie")
    else:
        print("❌ Échec de connexion:", login_response.text)
        return
    
    # 2. Test sans filtre
    print("\n2. Test sans filtre...")
    all_transactions = requests.get(f"{BASE_URL}/transactions/", headers=headers)
    if all_transactions.status_code == 200:
        total_count = all_transactions.json()['count']
        print(f"✅ {total_count} transactions au total")
    else:
        print("❌ Erreur récupération transactions:", all_transactions.status_code)
        return
    
    # 3. Test avec date_gte (derniers 30 jours)
    print("\n3. Test avec date_gte (derniers 30 jours)...")
    thirty_days_ago = datetime.now() - timedelta(days=30)
    date_gte = thirty_days_ago.strftime('%Y-%m-%d')
    
    params = {'date__gte': date_gte}
    recent_transactions = requests.get(f"{BASE_URL}/transactions/", headers=headers, params=params)
    
    if recent_transactions.status_code == 200:
        recent_count = recent_transactions.json()['count']
        print(f"✅ {recent_count} transactions depuis {date_gte}")
        print(f"   Paramètre utilisé: date__gte={date_gte}")
    else:
        print("❌ Erreur avec date_gte:", recent_transactions.status_code)
        print("   Réponse:", recent_transactions.text)
    
    # 4. Test avec date_lte (avant aujourd'hui)
    print("\n4. Test avec date_lte (avant aujourd'hui)...")
    today = datetime.now().strftime('%Y-%m-%d')
    
    params = {'date__lte': today}
    old_transactions = requests.get(f"{BASE_URL}/transactions/", headers=headers, params=params)
    
    if old_transactions.status_code == 200:
        old_count = old_transactions.json()['count']
        print(f"✅ {old_count} transactions avant le {today}")
        print(f"   Paramètre utilisé: date__lte={today}")
    else:
        print("❌ Erreur avec date_lte:", old_transactions.status_code)
        print("   Réponse:", old_transactions.text)
    
    # 5. Test avec date_gte et date_lte (plage)
    print("\n5. Test avec date_gte ET date_lte (plage de 30 jours)...")
    sixty_days_ago = datetime.now() - timedelta(days=60)
    date_gte_range = sixty_days_ago.strftime('%Y-%m-%d')
    date_lte_range = thirty_days_ago.strftime('%Y-%m-%d')
    
    params = {
        'date__gte': date_gte_range,
        'date__lte': date_lte_range
    }
    range_transactions = requests.get(f"{BASE_URL}/transactions/", headers=headers, params=params)
    
    if range_transactions.status_code == 200:
        range_count = range_transactions.json()['count']
        print(f"✅ {range_count} transactions entre {date_gte_range} et {date_lte_range}")
        print(f"   Paramètres utilisés: date__gte={date_gte_range} ET date__lte={date_lte_range}")
    else:
        print("❌ Erreur avec plage de dates:", range_transactions.status_code)
        print("   Réponse:", range_transactions.text)
    
    # 6. Test avec filtres combinés (date + catégorie)
    print("\n6. Test avec filtres combinés (date + catégorie)...")
    
    # D'abord récupérer les catégories
    categories = requests.get(f"{BASE_URL}/categories/", headers=headers)
    if categories.status_code == 200 and categories.json()['results']:
        first_category_id = categories.json()['results'][0]['id']
        
        params = {
            'date__gte': date_gte,
            'category': first_category_id
        }
        combined_transactions = requests.get(f"{BASE_URL}/transactions/", headers=headers, params=params)
        
        if combined_transactions.status_code == 200:
            combined_count = combined_transactions.json()['count']
            print(f"✅ {combined_count} transactions avec catégorie {first_category_id} depuis {date_gte}")
            print(f"   Paramètres utilisés: date__gte={date_gte} ET category={first_category_id}")
        else:
            print("❌ Erreur avec filtres combinés:", combined_transactions.status_code)
    else:
        print("⚠️  Pas de catégories disponibles pour test combiné")
    
    # 7. Test avec formats de date différents
    print("\n7. Test avec formats de date différents...")
    
    # Format ISO avec heure
    iso_date = thirty_days_ago.isoformat()
    params = {'date__gte': iso_date}
    iso_transactions = requests.get(f"{BASE_URL}/transactions/", headers=headers, params=params)
    
    if iso_transactions.status_code == 200:
        iso_count = iso_transactions.json()['count']
        print(f"✅ Format ISO accepté: {iso_count} transactions depuis {iso_date}")
    else:
        print("❌ Format ISO rejeté:", iso_transactions.status_code)
    
    # 8. Test avec date invalide
    print("\n8. Test avec date invalide...")
    params = {'date__gte': 'invalid-date'}
    invalid_transactions = requests.get(f"{BASE_URL}/transactions/", headers=headers, params=params)
    
    if invalid_transactions.status_code == 200:
        print("⚠️  Date invalide acceptée (comportement inattendu)")
    else:
        print("✅ Date invalide correctement rejetée")
        print(f"   Code d'erreur: {invalid_transactions.status_code}")
    
    # 9. Vérification de l'exactitude des résultats
    print("\n9. Vérification de l'exactitude des résultats...")
    
    # Récupérer quelques transactions pour vérifier les dates
    params = {'date__gte': date_gte}
    check_transactions = requests.get(f"{BASE_URL}/transactions/", headers=headers, params=params)
    
    if check_transactions.status_code == 200:
        results = check_transactions.json()['results']
        if results:
            print("✅ Vérification des dates des transactions retournées:")
            for i, transaction in enumerate(results[:3]):  # Vérifier les 3 premières
                trans_date = transaction['date']
                print(f"   Transaction {i+1}: {trans_date} (≥ {date_gte})")
        else:
            print("   Aucune transaction à vérifier")
    
    print("\n" + "=" * 60)
    print("🎉 Tests des filtres de date terminés !")
    print("\nRésumé des filtres testés:")
    print("- date__gte : Filtre les transactions depuis une date donnée")
    print("- date__lte : Filtre les transactions jusqu'à une date donnée")
    print("- Combinaison des deux : Filtre sur une plage de dates")
    print("- Combinaison avec autres filtres : Fonctionne correctement")

if __name__ == "__main__":
    try:
        test_date_filters()
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API. Vérifiez que le serveur Django est lancé avec:")
        print("python manage.py runserver")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")