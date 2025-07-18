#!/bin/sh

# Collect static files
echo "Collect static files"
if [ "$DJANGO_ENV" = "production" ]; then
    python manage.py collectstatic --noinput
fi

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000