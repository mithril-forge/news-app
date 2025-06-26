#!/bin/bash

# Simple production deployment script for VPS
set -e

echo "🚀 Starting production deployment..."

# Pull latest images and build
echo "🏗️  Building and pulling images..."
docker compose -f compose.prod.yml pull
docker compose -f compose.prod.yml build

# Start services
echo "🔧 Starting services..."
docker compose -f compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 5

# Get the public IP
PUBLIC_IP=$(curl -s -4 ifconfig.me || curl -s ipinfo.io/ip || echo "unknown")

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your application should be available at: http://$PUBLIC_IP"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker compose -f compose.prod.yml logs -f"
echo "  Stop: docker compose -f compose.prod.yml down"
echo "  Update: git pull && ./deploy.sh"
echo "  Database backup: docker compose -f compose.prod.yml exec postgres pg_dump -U postgres app_db > backup.sql"
echo ""
echo "🔒 When you get a domain:"
echo "  1. Point your domain to this server ($PUBLIC_IP)"
echo "  2. Edit caddy/Caddyfile and uncomment the domain section"
echo "  3. Update the domain name in the Caddyfile"
echo "  4. Uncomment port 443 in compose.prod.yml"
echo "  5. Run: docker compose -f compose.prod.yml restart caddy"
