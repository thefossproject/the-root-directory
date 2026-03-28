#!/bin/bash
set -e
uv run python manage.py collectstatic --noinput
uv run python manage.py migrate
exec uv run gunicorn the_root_directory.wsgi --bind 0.0.0.0:8000 --workers 5
