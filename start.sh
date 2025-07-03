#!/usr/bin/env bash
# Script de démarrage pour Render

echo "🚀 Starting FinTrack API..."

# Exécuter le setup post-déploiement
echo "📋 Running post-deployment setup..."
python post_deploy.py

# Démarrer le serveur Gunicorn
echo "🌐 Starting Gunicorn server..."
exec gunicorn fintrack.wsgi:application --bind 0.0.0.0:$PORT