#!/bin/bash
# Rebuild with Search Specialist Auto-Tool

echo "=========================================="
echo "🚀 Rebuild with Auto-Tool Enabled"
echo "=========================================="
echo ""
echo "🔧 Features:"
echo "   ✅ Search Specialist Auto-Tool"
echo "   ✅ Automatic Pinecone Search"
echo "   ✅ Auto-embedding Generation"
echo "   ✅ Low Threshold (0.08)"
echo ""

cd /home/node/.openclaw/workspace-unjai/docker

echo "📋 Checking files..."
for file in "../tools/search_specialist_tool.py" "../tools/search_specialist_tool.json"; do
    if [ -f "$file" ]; then
        echo "  ✅ $(basename $file)"
    else
        echo "  ❌ $(basename $file) missing"
        exit 1
    fi
done

echo ""
echo "🛑 Stopping old containers..."
docker-compose down 2>/dev/null
docker stop unjai-gateway 2>/dev/null
docker rm unjai-gateway 2>/dev/null

echo ""
echo "🏗️  Building with auto-tool..."
docker-compose build --no-cache line-gateway

echo ""
echo "🚀 Starting..."
docker-compose up -d

echo ""
echo "⏳ Waiting for initialization..."
sleep 5

echo ""
echo "📊 Status:"
docker-compose ps

echo ""
echo "📝 Checking auto-tool..."
docker exec unjai-gateway python3 -c "
import sys
sys.path.insert(0, '/app/tools')
try:
    from search_specialist_tool import SearchSpecialistTool
    tool = SearchSpecialistTool()
    print('✅ Auto-Tool loaded successfully')
    print(f'   Base URL: {tool.base_url}')
    print(f'   Namespace: {tool.pinecone_namespace}')
except Exception as e:
    print(f'❌ Error: {e}')
" 2>&1

echo ""
echo "=========================================="
echo "✅ Rebuild complete with Auto-Tool!"
echo ""
echo "Test in LINE:"
echo "  - ตรุษจีน"
echo "  - ความรัก"
echo "  - การให้อภัย"
echo ""
echo "Watch logs:"
echo "  docker-compose logs -f line-gateway | grep -E 'Auto-Tool|Found|video'"
echo "=========================================="
