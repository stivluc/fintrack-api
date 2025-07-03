#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Populate default categories
python manage.py populate_categories

# Populate demo data
python manage.py populate_demo_data

# Collect static files
python manage.py collectstatic --noinput