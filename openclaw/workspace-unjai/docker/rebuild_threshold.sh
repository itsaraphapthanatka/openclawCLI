#!/bin/bash
# Rebuild with Score Threshold Fix

echo "=========================================="
echo "🚀 Rebuild with Lower Score Threshold"
echo "=========================================="
echo ""
echo "🔧 Fix Applied:"
echo "   - min_score: 0.70 → 0.08"
echo "   - This allows low-similarity videos to be returned"
echo ""

cd /home/node/.openclaw/workspace-unjai/docker

echo "📋 Checking environment..."
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    exit 1
fi

echo ""
echo "🛑 Stopping old containers..."
docker-compose down 2>/dev/null
docker stop unjai-gateway 2>/dev/null
docker rm unjai-gateway 2>/dev/null

echo ""
echo "🏗️  Building gateway with threshold fix..."
docker-compose build --no-cache line-gateway

echo ""
echo "🚀 Starting..."
docker-compose up -d

echo ""
echo "⏳ Waiting..."
sleep 5

echo ""
echo "📊 Status:"
docker-compose ps

echo ""
echo "=========================================="
echo "✅ Rebuild complete!"
echo ""
echo "Now test in LINE with:"
echo "  - ตรุษจีน"
echo "  - ความรัก"
echo "  - การให้อภัย"
echo ""
echo "Videos should now appear (score threshold lowered)"
echo ""
echo "Watch logs:"
echo "  docker-compose logs -f line-gateway | grep -E 'Found|video|score'"
echo "=========================================="
