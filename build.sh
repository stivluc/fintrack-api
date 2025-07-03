#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip and setuptools
pip install --upgrade pip setuptools

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Populate default categories (only if needed)
python manage.py populate_categories || echo "Categories already exist"

# Populate demo data (only if needed)
python manage.py populate_demo_data || echo "Demo data already exists"

# Collect static files
python manage.py collectstatic --noinput