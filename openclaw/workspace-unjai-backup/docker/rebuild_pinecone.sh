#!/bin/bash
# Rebuild with Pinecone Search Fix

echo "=========================================="
echo "🚀 Rebuild with Pinecone Search Enabled"
echo "=========================================="
echo ""

cd /home/node/.openclaw/workspace-unjai/docker

echo "📋 Step 1: Verify configuration..."
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    exit 1
fi

# Check critical vars
for var in PINECONE_API_KEY PINECONE_INDEX_HOST BASE_URL OPENAI_API_KEY LINE_CHANNEL_ACCESS_TOKEN; do
    if grep -q "^${var}=" .env; then
        echo "  ✅ $var"
    else
        echo "  ⚠️  $var (will use default)"
    fi
done

echo ""
echo "🛑 Step 2: Stopping old containers..."
docker-compose down 2>/dev/null
docker-compose -f docker-compose.simple.yml down 2>/dev/null
docker stop unjai-gateway-simple unjai-gateway 2>/dev/null
docker rm unjai-gateway-simple unjai-gateway 2>/dev/null

echo ""
echo "🏗️  Step 3: Building gateway with Pinecone fix..."
docker-compose build --no-cache line-gateway

echo ""
echo "🚀 Step 4: Starting with Pinecone search enabled..."
docker-compose up -d

echo ""
echo "⏳ Step 5: Waiting for services..."
sleep 5

echo ""
echo "📊 Step 6: Checking status..."
docker-compose ps

echo ""
echo "📝 Step 7: Pinecone connection test..."
docker exec unjai-gateway python3 -c "
import sys
sys.path.insert(0, '/app/modules')
from line_orchestrator import SearchSpecialistConnector
import asyncio

async def test():
    c = SearchSpecialistConnector()
    print(f'✅ Search Specialist initialized')
    print(f'   Index: {c.index_host}')
    print(f'   Base URL: {c.base_url}')
    
    # Quick test
    results = await c.search_pinecone_by_text('ตรุษจีน', top_k=1)
    print(f'✅ Search test: Found {len(results)} videos')
    if results:
        print(f'   Sample URL: {results[0][\"clip_url\"][:60]}...')

asyncio.run(test())
" 2>&1 || echo "⚠️  Container test failed (may need more time)"

echo ""
echo "=========================================="
echo "✅ Rebuild complete!"
echo ""
echo "Test in LINE with queries like:"
echo "  - ตรุษจีน"
echo "  - ความรัก"
echo "  - การให้อภัย"
echo ""
echo "Watch logs:"
echo "  docker-compose logs -f line-gateway | grep -E 'Search|video|clip|Pinecone'"
echo "=========================================="
