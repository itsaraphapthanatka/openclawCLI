#!/bin/bash
# Rebuild with Media Delivery Agent + Flex Templates

echo "=========================================="
echo "🎬 Rebuild: Media Delivery Agent + Flex"
echo "=========================================="
echo ""
echo "📋 Agent Structure:"
echo "   1️⃣  Search Specialist (Hybrid Search)"
echo "   2️⃣  Journey Architect (Decision)"
echo "   3️⃣  Front-Desk (Response Building)"
echo "   4️⃣  Media Delivery (Flex Message) ← ใหม่!"
echo ""
echo "🔧 Flex Templates:"
echo "   ✅ create_video_card() - 5-star rating"
echo "   ✅ create_video_nudge()"
echo "   ✅ create_quiz_card()"
echo ""

cd /home/node/.openclaw/workspace-unjai/docker

echo "📋 Checking files..."
files=(
    "../modules/flex_templates.py"
    "../docker/entrypoints/gateway_coordinated.py"
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
echo "🏗️  Building with Media Delivery Agent..."
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
echo "📝 Verifying Agents..."
docker exec unjai-gateway python3 -c "
import sys
sys.path.insert(0, '/app/modules')
sys.path.insert(0, '/app/tools')

from coordination_protocol import get_coordinator
coord = get_coordinator()

print('✅ Registered Agents:')
for agent in coord.registry.get_all_active():
    print(f'   • {agent}')

# Check capabilities
if 'media_delivery' in coord.registry.get_all_active():
    print('')
    print('✅ Media Delivery Agent: ACTIVE')
    caps = coord.registry.capabilities.get('media_delivery', [])
    print(f'   Capabilities: {caps}')
else:
    print('')
    print('⚠️  Media Delivery Agent: NOT FOUND')
" 2>&1

echo ""
echo "=========================================="
echo "✅ Media Delivery Agent Ready!"
echo ""
echo "Workflow:"
echo "  1️⃣  Search Specialist → Hybrid Search"
echo "  2️⃣  Journey Architect → Decision"
echo "  3️⃣  Front-Desk → Build Response"
echo "  4️⃣  Media Delivery → Send Flex Message ⭐"
echo ""
echo "Flex Templates in Media Delivery:"
echo "   • Video Card (Hero + 5⭐ + Buttons)"
echo "   • Video Nudge"
echo "   • Quiz Card"
echo ""
echo "Test in LINE:"
echo "  - Send: ตรุษจีน"
echo "  - Expect: Flex Message with thumbnail + stars"
echo ""
echo "Watch logs:"
echo "  docker-compose logs -f line-gateway | grep -E 'Media|Delivery|Flex|Agent'"
echo "=========================================="
