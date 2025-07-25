#!/bin/sh
# Exit immediately if a command exits with a non-zero status.
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application in environment $ENVIRONMENT"

# Use Railway's PORT if available, otherwise default to 8000
PORT=${PORT:-8000}

if [ "$ENVIRONMENT" = "development" ]; then
  echo "Development mode detected, enabling hot reload..."
  # Modify the command to add the --reload flag for development
  ARGS="$@"
  if echo "$ARGS" | grep -q "uvicorn"; then
    # For uvicorn commands, append --reload and use PORT
    exec uvicorn main:app --host 0.0.0.0 --port $PORT --reload
  else
    # For other commands, execute normally
    exec "$@"
  fi
else
  # Production mode - use Railway's PORT
  exec uvicorn main:app --host 0.0.0.0 --port $PORT
fi

