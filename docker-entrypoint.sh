#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn FasadSiteDjango.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
