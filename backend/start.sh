#!/bin/bash
set -e

echo "Waiting for database to be ready..."
# Wait for postgres to be ready
until pg_isready -h postgres -p 5432 -U predico_user; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

