#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h $POSTGRES_HOST -U $POSTGRES_USER; do
  sleep 1
done

echo "PostgreSQL is ready!"
echo "Starting SYSAI backend..."

exec uvicorn app.main:app --host 0.0.0.0 --port 8000