#!/usr/bin/env python3
"""
Script de configuration initial pour FinTrack API
Usage: python setup_demo.py
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} terminé")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}")
        print(f"Sortie d'erreur: {e.stderr}")
        return False

def main():
    print("🚀 Configuration de FinTrack API")
    print("=" * 50)
    
    # Vérifier que le fichier .env existe
    if not os.path.exists('.env'):
        print("❌ Fichier .env manquant !")
        print("Veuillez copier .env.example vers .env et configurer DATABASE_URL")
        sys.exit(1)
    
    # Vérifier que DATABASE_URL est configuré
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.environ.get('DATABASE_URL'):
        print("❌ DATABASE_URL non configuré dans .env !")
        print("Veuillez ajouter votre URL Supabase dans le fichier .env")
        sys.exit(1)
    
    print("✅ Configuration .env détectée")
    
    # Étapes de configuration
    steps = [
        ("python manage.py migrate", "Migration de la base de données"),
        ("python manage.py populate_categories", "Création des catégories par défaut"),
        ("python manage.py populate_demo_data", "Création des données de démo"),
    ]
    
    for command, description in steps:
        if not run_command(command, description):
            print(f"\n❌ Échec de la configuration à l'étape: {description}")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Configuration terminée avec succès !")
    print("\n📝 Comptes créés :")
    print("   • Demo User : demo@fintrack.com / demo123")
    print("   • Admin     : admin@fintrack.com / admin123")
    print("\n🚀 Pour lancer l'API :")
    print("   python manage.py runserver")
    print("\n🧪 Pour tester l'API :")
    print("   python test_api.py")
    print("\n🔧 Interface admin :")
    print("   http://localhost:8000/admin/")

if __name__ == "__main__":
    main()