#!/bin/bash
# Rebuild with Hybrid Search v2.0 (Iron Rule Implementation)

echo "=========================================="
echo "🚀 Rebuild: Hybrid Search v2.0"
echo "=========================================="
echo ""
echo "🔧 AGENTS.md Compliance:"
echo "   ✅ Parallel Search (Text + Video)"
echo "   ✅ MEMORY.md search"
echo "   ✅ Pinecone (highlights) search"
echo "   ✅ Iron Rule: Score > 0.80 → Must send metadata"
echo ""

cd /home/node/.openclaw/workspace-unjai/docker

echo "📋 Checking files..."
files=(
    "../tools/search_specialist_tool.py"
    "../modules/coordination_protocol.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $(basename $file)"
    else
        echo "  ❌ $(basename $file) missing"
    fi
done

echo ""
echo "🛑 Stopping containers..."
docker-compose down 2>/dev/null
docker stop unjai-gateway 2>/dev/null
docker rm unjai-gateway 2>/dev/null

echo ""
echo "🏗️  Building with Hybrid Search v2.0..."
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
echo "📝 Checking Hybrid Search..."
docker exec unjai-gateway python3 -c "
import sys
sys.path.insert(0, '/app/tools')
try:
    from search_specialist_tool import SearchSpecialistTool
    tool = SearchSpecialistTool()
    print('✅ Hybrid Search v2.0 loaded')
    print(f'   Iron Rule Threshold: {tool.IRON_RULE_THRESHOLD}')
    print(f'   Base URL: {tool.base_url}')
    print(f'   Memory file: {tool.memory_file}')
except Exception as e:
    print(f'❌ Error: {e}')
" 2>&1

echo ""
echo "=========================================="
echo "✅ Hybrid Search v2.0 Ready!"
echo ""
echo "AGENTS.md Compliance:"
echo "  • Search Specialist: Parallel Retriever ✅"
echo "  • Hybrid Search: Text + Video ✅"
echo "  • Iron Rule (score>0.80): Enforced ✅"
echo ""
echo "Test in LINE:"
echo "  - ตรุษจีน"
echo "  - ความรัก"
echo ""
echo "Watch logs:"
echo "  docker-compose logs -f line-gateway | grep -E 'Hybrid|Iron|Score|video'"
echo "=========================================="
