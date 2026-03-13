#!/bin/bash
# Start Simple Gateway (No Swarm 15 Agents)

echo "=========================================="
echo "🚀 Nong Unjai Simple Gateway"
echo "=========================================="
echo ""
echo "⚠️  MODE: NO SWARM (15 Agents disabled)"
echo "✅ Direct LINE ↔ Pinecone connection"
echo ""

cd /home/node/.openclaw/workspace-unjai/docker

echo "📋 Checking configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    if grep -q "PINECONE_API_KEY=pcsk_" .env; then
        echo "✅ PINECONE_API_KEY configured"
    else
        echo "❌ PINECONE_API_KEY not found"
        exit 1
    fi
    if grep -q "BASE_URL=https://" .env; then
        echo "✅ BASE_URL configured"
    else
        echo "❌ BASE_URL not found"
        exit 1
    fi
else
    echo "❌ .env file not found"
    exit 1
fi

echo ""
echo "🛑 Stopping old containers..."
docker-compose -f docker-compose.simple.yml down 2>/dev/null || true

echo ""
echo "🏗️  Building Simple Gateway..."
docker-compose -f docker-compose.simple.yml build

echo ""
echo "🚀 Starting Simple Gateway..."
docker-compose -f docker-compose.simple.yml up -d

echo ""
echo "⏳ Waiting for startup..."
sleep 3

echo ""
echo "📊 Status:"
docker-compose -f docker-compose.simple.yml ps

echo ""
echo "📝 Logs (last 20 lines):"
docker-compose -f docker-compose.simple.yml logs --tail=20

echo ""
echo "=========================================="
echo "✅ Simple Gateway is running!"
echo ""
echo "Test commands:"
echo "  curl http://localhost:8000/health"
echo "  docker-compose -f docker-compose.simple.yml logs -f"
echo "=========================================="
