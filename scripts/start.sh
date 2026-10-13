#!/bin/sh
# start.sh: container start command.  Applies pending migrations, then runs gunicorn.
set -e

python manage.py migrate --noinput

exec gunicorn EQMacEmu_Players.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120 \
  --access-logfile -
