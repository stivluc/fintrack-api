#!/usr/bin/env python
"""
Script temporaire pour exécuter la population de données
À supprimer après utilisation
"""
import os
import django
from django.core.management import execute_from_command_line

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fintrack.settings.production')
django.setup()

if __name__ == '__main__':
    # Exécuter les commandes de population
    print("🚀 Population des catégories...")
    execute_from_command_line(['manage.py', 'populate_categories'])
    
    print("🚀 Population des données de démo...")
    execute_from_command_line(['manage.py', 'populate_demo_data'])
    
    print("✅ Population terminée !")