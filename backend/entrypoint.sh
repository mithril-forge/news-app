#!/bin/sh
# Exit immediately if a command exits with a non-zero status.
set -e

# Handle Docker secrets in production
if [ "$ENVIRONMENT" = "production" ]; then
  echo "Production environment detected, loading secrets..."
  if [ -f /run/secrets/gemini_api_key ]; then
    export GEMINI_API_KEY="$(cat /run/secrets/gemini_api_key)"
    echo "Gemini API key loaded from Docker secret"
  else
    echo "Warning: Gemini API key secret not found at /run/secrets/gemini_api_key"
  fi
fi

# Set up cron job to run daily at 1:00 AM
echo "Setting up scheduled task to run daily at 1:00 AM..."
# Create cron job
echo "0 1 * * * python3 /app/news_processing.py parse --days 1
0 2 * * 2 python3 /app/news_processing.py archive --days 30" > /tmp/crontab.tmp

crontab /tmp/crontab.tmp
rm /tmp/crontab.tmp

if command -v cron >/dev/null 2>&1; then
  service cron start 2>/dev/null || cron 2>/dev/null &
else
  service crond start 2>/dev/null || crond 2>/dev/null &
fi
echo "Scheduled task setup complete."


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

