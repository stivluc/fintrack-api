from django.http import JsonResponse
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import io
import sys

@csrf_exempt
@require_http_methods(["GET", "POST"])
def populate_data_view(request):
    """
    Vue temporaire pour exécuter la population de données
    À supprimer après utilisation
    """
    try:
        # Capturer la sortie des commandes
        output = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output
        
        # Exécuter les commandes de management
        call_command('populate_categories')
        call_command('populate_demo_data')
        
        # Restaurer stdout
        sys.stdout = old_stdout
        command_output = output.getvalue()
        
        return JsonResponse({
            'success': True,
            'message': 'Données populées avec succès !',
            'output': command_output
        })
        
    except Exception as e:
        # Restaurer stdout en cas d'erreur
        sys.stdout = old_stdout
        
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)