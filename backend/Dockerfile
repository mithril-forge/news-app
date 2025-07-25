FROM python:3.13-slim-bookworm

# Set working directory
WORKDIR /app
ENV TZ=Europe/Prague
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
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
COPY pyproject.toml uv.lock ./
COPY wheels/ wheels/

RUN uv export --format requirements-txt > requirements.txt
RUN uv pip install -r requirements.txt --system

# Copy application code
COPY . .

# Copy the entrypoint script into the container
COPY entrypoint_backend.sh /entrypoint_backend.sh
COPY entrypoint_dramatiq.sh /entrypoint_dramatiq.sh
# Make the entrypoint script executable
RUN chmod +x /entrypoint_backend.sh
RUN chmod +x /entrypoint_dramatiq.sh

# Expose port (Railway will override this with $PORT)
EXPOSE 8000

# Default command for Railway
CMD ["bash", "/entrypoint_backend.sh"]

