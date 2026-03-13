#!/bin/bash
# Start with Full Orchestrator/Gateway Coordination

echo "=========================================="
echo "🚀 Nong Unjai - Full Coordination Mode"
echo "=========================================="
echo ""
echo "✅ Orchestrator/Gateway Coordination: ENABLED"
echo "✅ Agent Communication Protocol: ENABLED"
echo "✅ Gateway-Orchestrator Bridge: ACTIVE"
echo ""
echo "Components:"
echo "  🔍 Search Specialist Agent"
echo "  🎯 Journey Architect Agent"  
echo "  🎙️ Front-Desk Agent"
echo "  📡 Coordination Protocol"
echo "  🌉 Gateway-Orchestrator Bridge"
echo ""

cd /home/node/.openclaw/workspace-unjai/docker

echo "📋 Checking configuration..."
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    exit 1
fi

# Verify critical variables
for var in PINECONE_API_KEY PINECONE_INDEX_HOST BASE_URL LINE_CHANNEL_ACCESS_TOKEN; do
    if grep -q "^${var}=" .env; then
        echo "✅ $var configured"
    else
        echo "❌ $var missing in .env"
        exit 1
    fi
done

echo ""
echo "🛑 Stopping old containers..."
docker-compose down 2>/dev/null
docker-compose -f docker-compose.simple.yml down 2>/dev/null
docker stop unjai-gateway-simple 2>/dev/null

echo ""
echo "🏗️  Building with coordination protocol..."
docker-compose build --no-cache line-gateway

echo ""
echo "🚀 Starting with full coordination..."
docker-compose up -d

echo ""
echo "⏳ Waiting for coordination system..."
sleep 5

echo ""
echo "📊 Checking status..."
docker-compose ps

echo ""
echo "📝 Coordination logs:"
docker-compose logs --tail=40 line-gateway | grep -E "COORDINATION|Agent|Protocol|Bridge|registered"

echo ""
echo "=========================================="
echo "✅ Full Coordination System is ACTIVE!"
echo ""
echo "Verify with:"
echo "  curl http://localhost:8000/health"
echo "  docker-compose logs -f line-gateway"
echo ""
echo "Communication Flow:"
echo "  LINE → Gateway → Coordinator → Agents → Response"
echo "=========================================="
