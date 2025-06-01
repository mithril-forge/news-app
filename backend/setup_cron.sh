#!/bin/bash

CONTAINER_NAME=${1:-"fastapi_backend"}

(
  crontab -l 2>/dev/null
  echo "0 6,18 * * * docker exec $CONTAINER_NAME python3 /app/input_news_trigger.py full-pipeline --days 1 --commit >> /var/log/news_processing.log 2>&1"
) | crontab -

echo "Cron job added for container: $CONTAINER_NAME"
