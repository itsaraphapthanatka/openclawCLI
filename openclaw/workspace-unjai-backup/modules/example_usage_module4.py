#!/usr/bin/env python3
"""
Example usage of Module 4: LINE Gateway
Nong Unjai AI System
"""

import asyncio
from module_4_line_gateway import (
    LineGateway,
    FlexMessageBuilder,
    create_app,
    UserSession,
    ParsedMessage
)


def example_1_flex_messages():
    """Example 1: Build Flex Messages"""
    print("=" * 70)
    print("Example 1: Flex Message Builder")
    print("=" * 70)
    
    builder = FlexMessageBuilder()
    
    # Video Card
    print("\n🎬 Video Card:")
    video_card = builder.create_video_card(
        title="การรักตัวเองตามพระคัมภีร์",
        description="คำสอนเกี่ยวกับการเห็นคุณค่าในตัวเองจากปฐมกาล 1:27",
        video_url="https://example.com/video.mp4",
        thumbnail_url="https://example.com/thumb.jpg",
        duration="10:23",
        scripture="ปฐมกาล 1:27",
        tags=["self-love", "healing", "identity"]
    )
    print(f"   Card type: {video_card['type']}")
    print(f"   Has thumbnail: {'hero' in video_card}")
    print(f"   Has footer button: {'footer' in video_card}")
    
    # Quiz Card
    print("\n🎯 Quiz Card:")
    quiz_card = builder.create_quiz_card(
        question="พระเยซูทรงให้คำสอนเรื่องอะไรบนภูเขา?",
        choices=[
            "คำอธิษฐาน",
            "คำเทศน์บนภูเขา",
            "อัศจรรย์",
            "การฟื้นคืนชีพ"
        ],
        quiz_id="quiz_001"
    )
    print(f"   Question: {quiz_card['body']['contents'][0]['text']}")
    print(f"   Choices: {len(quiz_card['footer']['contents'])}")
    
    # Progress Card
    print("\n📊 Progress Card:")
    progress_card = builder.create_progress_card(
        coins=150,
        r_score=72.5,
        circle_level=2,
        streak_days=5
    )
    print(f"   Title: {progress_card['header']['contents'][0]['text']}")
    print(f"   Stats sections: {len(progress_card['body']['contents'])}")
    
    # Carousel
    print("\n🎠 Carousel:")
    carousel = builder.create_carousel([video_card, quiz_card])
    print(f"   Type: {carousel['type']}")
    print(f"   Bubbles: {len(carousel['contents'])}")


def example_2_session_management():
    """Example 2: Session Management"""
    print("\n" + "=" * 70)
    print("Example 2: Session Management")
    print("=" * 70)
    
    from module_4_line_gateway import SessionManager
    
    # Note: Requires Redis running
    try:
        manager = SessionManager()
        
        user_id = "Utest123"
        
        # Get or create session
        print(f"\n👤 Getting session for {user_id}")
        session = manager.get_session(user_id)
        print(f"   Current persona: {session.current_persona}")
        print(f"   R-score: {session.r_score}")
        print(f"   Message count: {session.message_count}")
        
        # Add messages
        session.add_message("user", "สวัสดีค่ะ")
        session.add_message("assistant", "สวัสดีค่ะ! เป็นไงบ้างวันนี้?")
        
        # Update fields
        manager.update_session(
            user_id,
            current_persona=2,
            r_score=65.0
        )
        
        # Save
        manager.save_session(session)
        print(f"   ✓ Session saved")
        
        # Retrieve
        session2 = manager.get_session(user_id)
        print(f"   Retrieved persona: {session2.current_persona}")
        print(f"   History: {len(session2.conversation_history)} messages")
        
    except Exception as e:
        print(f"   ⚠️ Redis not available: {e}")
        print("   (This is OK for testing without Redis)")


def example_3_message_parsing():
    """Example 3: Parse LINE Events"""
    print("\n" + "=" * 70)
    print("Example 3: Message Parsing")
    print("=" * 70)
    
    # Mock LINE events
    events = [
        {
            "type": "message",
            "message": {"type": "text", "text": "สวัสดีค่ะ", "id": "123"},
            "source": {"userId": "Uxxx", "type": "user"},
            "timestamp": 1705315200000,
            "replyToken": "rtoken123"
        },
        {
            "type": "message",
            "message": {"type": "sticker", "stickerId": "1", "id": "124"},
            "source": {"userId": "Uxxx", "type": "user"},
            "timestamp": 1705315300000,
            "replyToken": "rtoken124"
        },
        {
            "type": "follow",
            "source": {"userId": "Unew", "type": "user"},
            "timestamp": 1705315400000,
            "replyToken": "rtoken125"
        },
        {
            "type": "postback",
            "postback": {"data": "quiz_answer|q1|A"},
            "source": {"userId": "Uxxx", "type": "user"},
            "timestamp": 1705315500000,
            "replyToken": "rtoken126"
        }
    ]
    
    gateway = LineGateway()
    
    for event in events:
        parsed = gateway.parse_event(event)
        if parsed:
            print(f"\n   Event: {event['type']}")
            print(f"   User: {parsed.user_id}")
            print(f"   Content: {parsed.content}")
            print(f"   Type: {parsed.message_type.value}")
            print(f"   Reply Token: {parsed.reply_token}")


async def example_4_response_types():
    """Example 4: Different Response Types"""
    print("\n" + "=" * 70)
    print("Example 4: Response Types")
    print("=" * 70)
    
    responses = [
        {
            "name": "Text",
            "data": {
                "type": "text",
                "content": "สวัสดีค่ะ! น้องอุ่นใจยินดีช่วยเหลือค่ะ"
            }
        },
        {
            "name": "Flex (Video)",
            "data": {
                "type": "flex",
                "alt_text": "Video: การรักตัวเอง",
                "flex_content": FlexMessageBuilder().create_video_card(
                    title="การรักตัวเอง",
                    description="คำสอนจากพระคัมภีร์",
                    video_url="https://example.com/video.mp4",
                    thumbnail_url="https://example.com/thumb.jpg"
                )
            }
        },
        {
            "name": "Quick Reply",
            "data": {
                "type": "quick_reply",
                "content": "เลือกได้เลยค่ะ!",
                "options": [
                    {"label": "🎥 ขอคลิป", "text": "ขอคลิปหนุนใจ"},
                    {"label": "📖 พระคัมภีร์", "text": "ข้อพระคัมภีร์"},
                    {"label": "🎯 ทำควิซ", "text": "อยากทำควิซ"},
                ]
            }
        },
        {
            "name": "Image",
            "data": {
                "type": "image",
                "url": "https://example.com/image.jpg",
                "thumbnail": "https://example.com/thumb.jpg"
            }
        }
    ]
    
    for resp in responses:
        print(f"\n📤 {resp['name']}:")
        print(f"   Type: {resp['data']['type']}")
        if 'content' in resp['data']:
            print(f"   Content: {resp['data']['content'][:50]}...")


def example_5_crisis_scenario():
    """Example 5: Crisis Handling"""
    print("\n" + "=" * 70)
    print("Example 5: Crisis Handling")
    print("=" * 70)
    
    messages = [
        ("สวัสดีค่ะ", False, "Normal greeting"),
        ("วันนี้รู้สึกนอยๆ", False, "Sad but not crisis"),
        ("อยากตาย ไม่อยากอยู่แล้ว", True, "CRISIS - Emergency"),
        ("ไม่ไหวแล้ว มืดแปดด้าน", True, "CRISIS - Emergency"),
        ("เหนื่อยจัง", False, "Tired but manageable"),
    ]
    
    for msg, is_crisis, desc in messages:
        status = "🚨" if is_crisis else "✅"
        print(f"\n   {status} '{msg}'")
        print(f"      → {desc}")


def example_6_integration_flow():
    """Example 6: Integration with Other Modules"""
    print("\n" + "=" * 70)
    print("Example 6: Integration Flow")
    print("=" * 70)
    
    print("""
📋 Full Integration Flow:

1️⃣  User sends: "วันนี้รู้สึกนอยๆ"
    ↓
2️⃣  LINE Gateway receives webhook
    ↓
3️⃣  Parse event → ParsedMessage
    ↓
4️⃣  Get UserSession from Redis
    ↓
5️⃣  Check Crisis? → NLP Processor
    ↓
6️⃣  Analyze sentiment & intent
    - Sentiment: NEGATIVE (-0.6)
    - Intent: emotional_support
    - R-Score: 45
    - Crisis: None
    ↓
7️⃣  Select Persona 2 (Healing)
    ↓
8️⃣  Search Knowledge Base
    - Query: "นอยๆ เศร้า กำลังใจ"
    - Circle 1 (Self)
    - Top result: "การรักตัวเองตามพระคัมภีร์"
    ↓
9️⃣  Build Flex Message (Video Card)
    ↓
🔟 Send reply to LINE
    
💬 Response:
    "อุ่นใจเข้าใจความรู้สึกของคุณพี่ค่ะ..."
    [Video Card with thumbnail]
    [Quick Reply: ดูคลิปอื่น | ทำควิซ | คุยต่อ]
    """)


async def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("💬 Module 4: LINE Gateway - Examples")
    print("=" * 70)
    
    try:
        example_1_flex_messages()
        example_2_session_management()
        example_3_message_parsing()
        await example_4_response_types()
        example_5_crisis_scenario()
        example_6_integration_flow()
        
        print("\n" + "=" * 70)
        print("✅ All examples completed!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
