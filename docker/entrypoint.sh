#!/bin/sh
set -e

# Run Alembic migrations in production before starting the API server.
if [ "${ENVIRONMENT}" = "production" ] && [ "${AUTO_CREATE_SCHEMA}" = "false" ]; then
  echo "Running database migrations..."
  alembic -c /app/alembic.ini upgrade head
fi

exec "$@"
