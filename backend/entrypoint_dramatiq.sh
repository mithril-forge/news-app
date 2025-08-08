#!/bin/sh
# Exit immediately if a command exits with a non-zero status.
set -e

periodiq dramatiq_tasks > /var/log/periodiq.log 2>&1 &
exec "$@"
