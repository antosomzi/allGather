#!/bin/bash
echo "Waiting for database..."
until pg_isready -h db -p 5432 -U postgres; do
  echo "DB not ready, waiting..."
  sleep 2
done
echo "Database ready! Running migrations..."
alembic upgrade head
echo "Migrations complete!"