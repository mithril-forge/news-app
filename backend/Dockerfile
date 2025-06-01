FROM python:3.13-slim-bookworm

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies including PostgreSQL requirements
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
        postgresql-client \
        curl \
        cron \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install `uv`
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy poetry configuration files and wheels directory
COPY pyproject.toml poetry.lock* ./
COPY wheels/ wheels/

RUN uv pip install --system poetry \
    && uv pip install --system poetry-plugin-export \
    && poetry export --without-hashes --only main --format requirements.txt > requirements.txt \
    # Possible additional exports for development and production
    # && poetry export --without-hashes --only dev --format requirements.txt > requirements-dev.txt \
    # && poetry export --without-hashes --only production --format requirements.txt > requirements-production.txt \
    && uv pip install --system -r requirements.txt \
    && rm -rf wheels/ \
    && rm -f pyproject.toml poetry.lock

# Copy application code
COPY . .

# Expose port
EXPOSE 8000
# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
