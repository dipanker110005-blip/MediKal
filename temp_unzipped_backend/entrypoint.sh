#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# If PostgreSQL env variables are set, wait for DB port to be ready
if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
  echo "Waiting for PostgreSQL database at $DB_HOST:$DB_PORT..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 0.5
  done
  echo "PostgreSQL database is active and accepting connections!"
fi

# Run migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Seed database
echo "Seeding production database with initial data..."
python manage.py seed_data

# Collect static files
echo "Collecting static assets..."
python manage.py collectstatic --noinput

# Start Gunicorn WSGI server
echo "Starting Gunicorn server on 0.0.0.0:${PORT:-8000}..."
exec gunicorn medikal_backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3
