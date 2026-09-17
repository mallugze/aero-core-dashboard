#!/bin/sh
set -e

echo '[INFO] Running database migrations...'
python manage.py migrate --noinput

echo '[INFO] Collecting static files...'
python manage.py collectstatic --noinput

echo '[INFO] Starting Gunicorn application server on 0.0.0.0:8000...'
exec gunicorn aero_core.wsgi:application     --bind 0.0.0.0:8000     --workers 2     --threads 2     --timeout 120
