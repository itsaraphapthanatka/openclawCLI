#!/bin/bash
# Rebuild with Flex Message Templates

echo "=========================================="
echo "🎨 Rebuild: Flex Message Templates"
echo "=========================================="
echo ""
echo "🔧 Features Added:"
echo "   ✅ Video Card Template (5-star rating)"
echo "   ✅ Video Nudge Template"
echo "   ✅ Quiz Card Template"
echo "   ✅ Text Card Template"
echo "   ✅ Error Card Template"
echo ""

cd /home/node/.openclaw/workspace-unjai/docker

echo "📋 Checking files..."
files=(
    "../modules/flex_templates.py"
    "../docker/entrypoints/gateway_coordinated.py"
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
echo "🏗️  Building with Flex Templates..."
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
echo "📝 Testing Flex Templates..."
docker exec unjai-gateway python3 -c "
import sys
sys.path.insert(0, '/app/modules')
try:
    from flex_templates import FlexMessageBuilder
    builder = FlexMessageBuilder()
    
    test_video = {
        'title': 'ตรุษจีนกับคริสเตียน',
        'full_url': 'https://nongaunjai.febradio.org/static/clips/test.mp4',
        'thumbnail': 'https://via.placeholder.com/800x520',
        'score': 0.823,
        'transcript': 'การเฉลิมฉลองตรุษจีน',
        'video_url': 'https://youtube.com/watch?v=test'
    }
    
    card = builder.create_video_card(test_video)
    print('✅ Flex Templates loaded successfully')
    print(f'   Template type: {card[\"type\"]}')
    print(f'   Has hero: {\"hero\" in card}')
    print(f'   Has footer: {\"footer\" in card}')
    print(f'   Buttons in footer: {len(card.get(\"footer\", {}).get(\"contents\", []))}')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
" 2>&1

echo ""
echo "=========================================="
echo "✅ Flex Templates Ready!"
echo ""
echo "Templates available:"
echo "  • create_video_card() - Video with 5-star rating"
echo "  • create_video_nudge() - Nudge card"
echo "  • create_quiz_card() - Quiz after video"
echo "  • create_text_card() - Text content card"
echo "  • create_error_card() - Error message"
echo ""
echo "Test in LINE:"
echo "  - Send any query to get video card"
echo ""
echo "Watch logs:"
echo "  docker-compose logs -f line-gateway | grep -E 'Flex|video|card'"
echo "=========================================="
