# Deployment Guide

This project supports both development and production environments with single-command deployment.

## Development Environment

### Prerequisites
- Docker and Docker Compose
- GEMINI_API_KEY environment variable

### Quick Start
```bash
# Build and start development environment
make dev-all

# Or step by step:
make dev-build  # Build containers
make dev-up     # Start services
```

### Development Features
- Hot reload for both frontend and backend
- Volume mounts for live code editing
- Debug-friendly configuration
- Direct port access (frontend:3000, backend:8000, postgres:5432)

### Managing Development Environment
```bash
make dev-down   # Stop all services
make dev-logs   # View logs from all containers
make help       # Show all available commands
```

## Production Environment

### Prerequisites
- Docker Swarm mode initialized
- Required secrets created (see below)

### Secret Management
Before deploying to production, create required secrets:
```bash
# Database password
echo "your_secure_db_password" | docker secret create db_password -

# Gemini API key
echo "your_gemini_api_key" | docker secret create gemini_api_key -
```

### Quick Start
```bash
# Build and deploy production environment
make prod-all

# Or step by step:
make prod-build   # Build production images
make prod-deploy  # Deploy to Docker Swarm
```

### Production Features
- Docker Swarm deployment with multiple replicas
- Secret management for sensitive data
- Production-optimized frontend builds
- Rolling updates
- Overlay networking

### Managing Production Environment
```bash
make prod-remove  # Remove production stack
docker stack ps app  # Check stack status
docker service logs app_frontend  # View service logs
```

## Environment Configuration

### Development (`envs/common_dev.env`)
- Local development database connection
- Hot reload enabled
- Debug configuration

### Production (`envs/common_prod.env`)
- Production database connection
- Optimized for performance
- Secret-based authentication

## Troubleshooting

### Common Issues
1. **GEMINI_API_KEY not set**: Export the environment variable before running dev commands
2. **Docker Swarm not initialized**: Run `docker swarm init` before production deployment
3. **Secrets missing**: Create required secrets before running `make prod-deploy`

### Validating Configuration
Run the validation script to check if everything is properly configured:
```bash
# This will be integrated into the deployment process
docker compose -f docker-compose.base.yml -f docker-compose.dev.yml config --quiet
docker compose -f docker-compose.base.yml -f docker-compose.prod.yml config --quiet
```