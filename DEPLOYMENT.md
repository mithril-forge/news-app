# Deployment Guide

This guide explains how to deploy the news app in both development and production environments.

## Prerequisites

- Docker and Docker Compose installed
- Make utility installed
- Git repository cloned

## Development Environment

### Quick Start

Start the development environment with one command:

```bash
make dev-up
```

This will:
- Ask for your GEMINI_API_KEY if not set as an environment variable
- Start all services in development mode with hot reloading
- Expose services on localhost:3000 (frontend) and localhost:8000 (backend)

### Development Commands

```bash
make help                # Show all available commands
make dev-up             # Start development environment
make dev-down           # Stop development environment  
make dev-build          # Rebuild development containers
make dev-logs           # Show logs from all containers
```

### Environment Variables (Development)

All development environment variables are pre-configured in `envs/common_dev.env`:
- Database: PostgreSQL with default credentials
- GEMINI_API_KEY: Prompted during startup or set via environment variable

## Production Environment

### Quick Start

1. **First time setup**: Create production environment file:
   ```bash
   make prod-deploy
   ```
   This will create `.env` from `.env.example` and prompt you to edit it.

2. **Edit the `.env` file** with your production values:
   ```bash
   vim .env  # or your preferred editor
   ```

3. **Deploy to production**:
   ```bash
   make prod-deploy
   ```

### Alternative: Simple Production Deployment

For a simple VPS deployment, you can also use:

```bash
make prod-deploy-simple
```

This uses the `deploy.sh` script which provides helpful deployment feedback.

### Production Commands

```bash
make prod-build         # Build production images
make prod-deploy        # Deploy to production using Docker Compose
make prod-deploy-simple # Deploy using deploy.sh script
make prod-remove        # Stop and remove production stack
make prod-all           # Build and deploy in one command
```

### Environment Variables (Production)

Production requires a `.env` file with:

```bash
# Database
POSTGRES_PASSWORD=your_secure_database_password_here

# API Keys  
GEMINI_API_KEY=your_gemini_api_key_here
```

Copy `.env.example` to `.env` and update the values.

## Architecture

### Development
- Uses `compose.base.yml` + `compose.yml`
- Hot reloading enabled
- Local volumes mounted for development
- All services exposed on localhost

### Production
- Uses `compose.base.yml` + `compose.prod.yml`
- Includes Caddy reverse proxy
- Production-optimized builds
- Environment-specific configuration

## Troubleshooting

### Development Issues

1. **GEMINI_API_KEY not set**: The command will prompt you for it
2. **Port conflicts**: Make sure ports 3000, 8000, and 5432 are free
3. **Build failures**: Check internet connection and retry with `make dev-build`

### Production Issues

1. **Missing .env file**: Run `make prod-deploy` to create from template
2. **Database connection**: Verify POSTGRES_PASSWORD in .env
3. **API issues**: Check GEMINI_API_KEY in .env

### Viewing Logs

```bash
# Development
make dev-logs

# Production
docker compose -f compose.base.yml -f compose.prod.yml logs -f
```

## File Structure

```
├── Makefile                    # Build and deployment commands
├── .env.example               # Production environment template
├── compose.base.yml           # Common Docker services
├── compose.yml                # Development overrides
├── compose.prod.yml           # Production overrides
├── deploy.sh                  # Alternative deployment script
└── envs/
    ├── common_dev.env         # Development environment
    └── common_prod.env        # Production environment base
```