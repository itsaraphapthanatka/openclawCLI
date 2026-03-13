#!/bin/bash
# Switch back to Swarm 15 Agents mode

echo "=========================================="
echo "🚀 Nong Unjai - Swarm 15 Agents Mode"
echo "=========================================="
echo ""
echo "✅ Enabling: Search Specialist Agent"
echo "✅ Enabling: Swarm 15 Agents"
echo "✅ Enabling: Journey Architect"
echo "✅ Enabling: Front-Desk Agent"
echo ""

cd /home/node/.openclaw/workspace-unjai/docker

echo "📋 Checking configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
else
    echo "❌ .env file not found"
    exit 1
fi

echo ""
echo "🛑 Stopping Simple Gateway..."
docker-compose -f docker-compose.simple.yml down 2>/dev/null || true
docker stop unjai-gateway-simple 2>/dev/null || true

echo ""
echo "🛑 Stopping old Swarm containers..."
docker-compose down 2>/dev/null || true

echo ""
echo "🏗️  Building Swarm Gateway..."
docker-compose build line-gateway

echo ""
echo "🚀 Starting Swarm 15 Agents..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services..."
sleep 5

echo ""
echo "📊 Status:"
docker-compose ps

echo ""
echo "📝 Logs (last 30 lines):"
docker-compose logs --tail=30 line-gateway

echo ""
echo "=========================================="
echo "✅ Swarm 15 Agents is running!"
echo ""
echo "Test commands:"
echo "  curl http://localhost:8000/health"
echo "  docker-compose logs -f line-gateway"
echo "=========================================="
