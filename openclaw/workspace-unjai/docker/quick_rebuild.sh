#!/bin/bash
# Quick rebuild and test script

echo "=========================================="
echo "🔧 Nong Unjai Quick Rebuild"
echo "=========================================="

cd /home/node/.openclaw/workspace-unjai/docker

echo ""
echo "📋 Step 1: Checking .env file..."
if grep -q "PINECONE_API_KEY=pcsk_" .env; then
    echo "✅ .env has PINECONE_API_KEY"
else
    echo "❌ .env missing PINECONE_API_KEY"
    exit 1
fi

if grep -q "BASE_URL=https://" .env; then
    echo "✅ .env has BASE_URL"
else
    echo "❌ .env missing BASE_URL"
    exit 1
fi

echo ""
echo "🛑 Step 2: Stopping old containers..."
docker-compose down

echo ""
echo "🏗️  Step 3: Building new image..."
docker-compose build line-gateway

echo ""
echo "🚀 Step 4: Starting services..."
docker-compose up -d

echo ""
echo "⏳ Step 5: Waiting for services to start..."
sleep 5

echo ""
echo "📊 Step 6: Checking logs..."
docker-compose logs --tail=20 line-gateway

echo ""
echo "=========================================="
echo "✅ Rebuild complete!"
echo ""
echo "Test commands:"
echo "  docker-compose logs -f line-gateway"
echo "  docker exec unjai-gateway python -c 'import os; print(os.getenv(\"BASE_URL\"))'"
echo "=========================================="
