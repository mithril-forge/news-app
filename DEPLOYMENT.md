# News App Deployment Guide

This guide provides comprehensive instructions for deploying the News App in both development and production environments with complete environment separation and single-command deployment.

## Prerequisites

- Docker and Docker Compose v2
- Make (for using Makefile commands)
- Git (for version control)

## Environment Architecture

The application supports two distinct environments:

### Development Environment
- **Purpose**: Local development with hot reload and debugging
- **Database**: Local PostgreSQL with exposed ports
- **Secrets**: Environment variables in plain text
- **Frontend**: Development build with hot reload
- **Backend**: Volume-mounted source code for live editing

### Production Environment
- **Purpose**: Production deployment with Docker Swarm
- **Database**: PostgreSQL without exposed ports
- **Secrets**: Docker secrets for sensitive data
- **Frontend**: Production-optimized build
- **Backend**: Compiled application with structured logging

## Quick Start

### Development Environment

```bash
# Build and start complete development environment
make dev-all

# Or step by step:
make dev-build    # Build containers
make dev-up       # Start services
make dev-logs     # View logs
make dev-down     # Stop services
```

### Production Environment

```bash
# Build and deploy complete production environment
make prod-all

# Or step by step:
make prod-build   # Build production images
make prod-deploy  # Deploy to Docker Swarm
make prod-status  # Check deployment status
make prod-logs    # View production logs
```

## Environment Configuration

### Development Configuration (`envs/common_dev.env`)

```bash
POSTGRES_DB=app_db
POSTGRES_USER=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_PASSWORD=postgres
ENVIRONMENT=development
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CONTAINER_API_URL=http://backend:8000
FRONTEND_URL=http://localhost:3000
LOCAL_ARCHIVE_FOLDER=/tmp/archive_folder
GEMINI_API_KEY=your_gemini_api_key_here
```

### Production Configuration (`envs/common_prod.env`)

```bash
POSTGRES_DB=app_db
POSTGRES_USER=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
ENVIRONMENT=production
NEXT_PUBLIC_API_URL=http://185.215.165.121:8000
NEXT_PUBLIC_CONTAINER_API_URL=http://backend:8000
FRONTEND_URL=http://localhost:3000
LOCAL_ARCHIVE_FOLDER=/tmp/archive_folder
```

**Note**: In production, sensitive values like `POSTGRES_PASSWORD` and `GEMINI_API_KEY` are provided via Docker secrets.

## Docker Compose Structure

The application uses a multi-file Docker Compose structure:

- **`compose.base.yml`**: Base services configuration shared between environments
- **`compose.yml`**: Development-specific overrides and configurations
- **`compose.prod.yml`**: Production-specific overrides with secrets and swarm deployment

## Secret Management

### Development
Secrets are stored as plain text environment variables in `envs/common_dev.env`.

### Production
Secrets are managed via Docker Swarm secrets:

```bash
# Secrets are created automatically during deployment
# You'll be prompted to enter:
# - Database password
# - Gemini API key

# To manually manage secrets:
make prod-secrets-remove  # Remove all secrets (use with caution)
```

## Available Make Commands

### Development Commands
- `make dev-build` - Build development containers
- `make dev-up` - Start development environment
- `make dev-down` - Stop development environment
- `make dev-logs` - Show development logs
- `make dev-restart` - Restart development environment
- `make dev-all` - **Build and start complete development environment**

### Production Commands
- `make prod-build` - Build production images
- `make prod-deploy` - Deploy to production (Docker Swarm)
- `make prod-status` - Show production stack status
- `make prod-logs` - Show production logs
- `make prod-remove` - Remove production stack
- `make prod-secrets-remove` - Remove production secrets
- `make prod-all` - **Build and deploy complete production environment**

### Utility Commands
- `make clean` - Clean up unused Docker resources
- `make validate` - Validate Docker Compose configurations
- `make help` - Show all available commands

## Service Access

### Development Environment
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Database**: localhost:5432 (accessible for debugging)

### Production Environment
- **Frontend**: http://185.215.165.121:80 (via Caddy reverse proxy)
- **Backend API**: http://185.215.165.121:8000 (via Caddy reverse proxy)
- **Database**: Internal network only (no external access)

## Troubleshooting

### Common Issues

#### Development Environment

**Issue**: GEMINI_API_KEY not set
```bash
# Solution: Set the API key in envs/common_dev.env
# Or provide it when prompted during `make dev-up`
```

**Issue**: Port conflicts
```bash
# Solution: Stop other services using ports 3000, 8000, or 5432
sudo lsof -i :3000,:8000,:5432
```

**Issue**: Database connection failed
```bash
# Solution: Ensure PostgreSQL container is healthy
docker compose -f compose.base.yml -f compose.yml ps
make dev-logs
```

#### Production Environment

**Issue**: Docker Swarm not initialized
```bash
# Solution: Initialize Docker Swarm
docker swarm init
```

**Issue**: Secrets already exist
```bash
# Solution: Remove existing secrets or use existing ones
make prod-secrets-remove
# Or manually remove specific secrets:
docker secret rm db_password gemini_api_key
```

**Issue**: Service deployment failed
```bash
# Solution: Check service status and logs
make prod-status
make prod-logs
```

### Validation

Before deployment, validate your configurations:

```bash
# Validate both development and production configurations
make validate

# Check specific configuration
docker compose -f compose.base.yml -f compose.yml config
docker compose -f compose.base.yml -f compose.prod.yml config
```

### Logs and Monitoring

```bash
# Development logs
make dev-logs

# Production logs
make prod-logs

# Specific service logs in production
docker service logs news-app_backend
docker service logs news-app_frontend
docker service logs news-app_postgres
```

## Security Considerations

### Development
- Database password is in plain text (acceptable for local development)
- All ports are exposed for debugging
- Source code is volume-mounted

### Production
- All sensitive data uses Docker secrets
- Database is not exposed externally
- Frontend serves optimized production build
- Reverse proxy (Caddy) handles external traffic
- Services run with restart policies and health checks

## Maintenance

### Updating the Application

1. **Pull latest changes**:
   ```bash
   git pull origin main
   ```

2. **Development**:
   ```bash
   make dev-down
   make dev-all
   ```

3. **Production**:
   ```bash
   make prod-all  # This will perform rolling updates
   ```

### Cleaning Up

```bash
# Clean Docker resources
make clean

# Remove development environment
make dev-down

# Remove production stack
make prod-remove
```

### Backup and Recovery

```bash
# Backup production database
docker exec news-app_postgres pg_dump -U postgres app_db > backup.sql

# Restore database
docker exec -i news-app_postgres psql -U postgres app_db < backup.sql
```

## Architecture Benefits

1. **Complete Environment Separation**: Development and production environments are completely isolated
2. **Single-Command Deployment**: `make dev-all` and `make prod-all` handle everything
3. **Proper Secret Management**: Production uses Docker secrets, development uses environment files
4. **Zero Hidden Dependencies**: All requirements are explicitly defined and automatically handled
5. **Production-Ready**: Includes reverse proxy, health checks, and rolling updates
6. **Developer-Friendly**: Hot reload, exposed ports, and volume mounts for development