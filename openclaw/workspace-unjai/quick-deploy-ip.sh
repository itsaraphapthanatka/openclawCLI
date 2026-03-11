#!/bin/bash
# Quick deploy for IP: 136.110.50.115

IP="136.110.50.115"

echo "🚀 Nong Unjai AI - Quick Deploy for IP: $IP"
echo ""

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "📦 Starting services..."
cd docker

# Create .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env <<EOF
# IP Configuration
DOMAIN=$IP
USE_SSL=false

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=unjai
POSTGRES_USER=unjai
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d '\n')

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d '\n')

# Services
GATEWAY_PORT=8000
ORCHESTRATOR_PORT=8001
ANALYTICS_PORT=8002
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# Logging
LOG_LEVEL=INFO
EOF
    echo "✅ .env file created"
fi

# Start services
echo "🐳 Starting Docker containers..."
docker-compose -f docker-compose.yml -f docker-compose.ip.yml up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check health
echo ""
echo "🔍 Checking health..."
if curl -s http://$IP:8000/health > /dev/null 2>&1; then
    echo "✅ Gateway is healthy"
else
    echo "⚠️  Gateway may still be starting..."
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ✅ Deployment Complete!                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Your system is running at:"
echo ""
echo "   Gateway:   http://$IP:8000"
echo "   Health:    http://$IP:8000/health"
echo "   Analytics: http://$IP:8002/dashboard"
echo ""
echo "📋 Useful commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop:         docker-compose down"
echo "   Restart:      docker-compose restart"
echo ""
echo "⚠️  IMPORTANT: LINE Webhook requires HTTPS!"
echo ""
echo "   To use with LINE, you have 3 options:"
echo ""
echo "   1️⃣  Cloudflare Tunnel (Recommended):"
echo "       ./deploy-ip.sh $IP cloudflare"
echo ""
echo "   2️⃣  Ngrok (Temporary):"
echo "       ./deploy-ip.sh $IP ngrok"
echo ""
echo "   3️⃣  Buy a domain and use Let's Encrypt:"
echo "       ./deploy-production.sh production all"
echo ""
