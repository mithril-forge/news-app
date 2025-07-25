#!/bin/sh
# Exit immediately if a command exits with a non-zero status.
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application in environment $ENVIRONMENT"
if [ "$ENVIRONMENT" = "development" ]; then
  echo "Development mode detected, enabling hot reload..."
  # Modify the command to add the --reload flag for development
  ARGS="$@"
  if echo "$ARGS" | grep -q "uvicorn"; then
    # For uvicorn commands, append --reload
    exec $@ --reload
  else
    # For other commands, execute normally
    exec "$@"
  fi
else
  # Normal production mode
  exec "$@"
fi
