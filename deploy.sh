#!/bin/bash

# Simple production deployment script for VPS
set -e

echo "🚀 Starting production deployment..."

# Create necessary directories
mkdir -p secrets caddy
cp ../secrets/db_password.txt secrets/
cp ../secrets/gemini_api_key.txt secrets/

# Check if secrets exist
if [ ! -f "secrets/db_password.txt" ]; then
    echo "❌ Please create secrets/db_password.txt with your database password"
    echo "   Example: echo 'your_strong_password' > secrets/db_password.txt"
    exit 1
fi

if [ ! -f "secrets/gemini_api_key.txt" ]; then
    echo "❌ Please create secrets/gemini_api_key.txt with your Gemini API key"
    echo "   Example: echo 'your_api_key' > secrets/gemini_api_key.txt"
    exit 1
fi

if [ ! -f "caddy/Caddyfile" ]; then
    echo "❌ Please create caddy/Caddyfile with your Caddy configuration"
    exit 1
fi

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
