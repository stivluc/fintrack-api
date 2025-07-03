from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import os

def health_check(request):
    """Health check endpoint pour diagnostiquer les problèmes"""
    try:
        # Test de connexion DB
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "✅ Connected"
    except Exception as e:
        db_status = f"❌ Error: {str(e)}"
    
    # Vérifier les variables d'environnement
    env_vars = {
        'DATABASE_URL': '✅ Set' if os.environ.get('DATABASE_URL') else '❌ Missing',
        'SECRET_KEY': '✅ Set' if os.environ.get('SECRET_KEY') else '❌ Missing',
        'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE', '❌ Missing'),
    }
    
    return JsonResponse({
        'status': 'healthy' if 'Connected' in db_status else 'unhealthy',
        'database': db_status,
        'environment': env_vars,
        'debug': settings.DEBUG,
    })