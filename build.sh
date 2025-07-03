#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip and setuptools
pip install --upgrade pip setuptools

# Install dependencies
pip install -r requirements.txt

# Use SQLite for build process (Render can't access external DBs during build)
export DATABASE_URL="sqlite:///build.db"

# Run migrations with SQLite
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

echo "Build completed successfully - runtime will use real DATABASE_URL"