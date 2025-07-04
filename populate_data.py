#!/usr/bin/env python
"""
Script temporaire pour exécuter la population de données
À supprimer après utilisation
"""
import os
import django
from django.core.management import call_command

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fintrack.settings')
django.setup()

if __name__ == '__main__':
    # Exécuter les commandes de population
    print("🚀 Population des catégories...")
    call_command('populate_categories')
    
    print("🚀 Population des données de démo...")
    call_command('populate_demo_data')
    
    print("✅ Population terminée !")
