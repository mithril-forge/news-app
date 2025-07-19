#!/bin/sh
# Exit immediately if a command exits with a non-zero status.
set -e

echo "Running database migrations..."
alembic upgrade head
periodiq dramatiq_tasks > /var/log/periodiq.log 2>&1 &
exec "$@"


