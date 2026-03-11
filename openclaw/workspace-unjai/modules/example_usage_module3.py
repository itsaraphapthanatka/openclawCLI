#!/usr/bin/env python3
"""
Example usage of Module 3: Main Orchestrator
Nong Unjai AI System
"""

import asyncio
from module_3_main_orchestrator import (
    MainOrchestrator,
    OrchestratedLineGateway,
    OrchestratorConfig,
    WorkflowContext
)
from module_4_line_gateway import UserSession


def example_1_basic_usage():
    """Example 1: Basic Orchestrator Usage"""
    print("=" * 70)
    print("Example 1: Basic Orchestrator Usage")
    print("=" * 70)
    
    async def run():
        orchestrator = MainOrchestrator()
        
        # Test different messages
        test_cases = [
            ("สวัสดีค่ะ", "New user greeting"),
            ("วันนี้รู้สึกนอยๆ", "Emotional support"),
            ("ยอห์น 3:16 ว่าอะไร", "Bible question"),
            ("ขอคลิปหนุนใจ", "Video request"),
            ("อยากตาย ไม่อยากอยู่แล้ว", "Crisis"),
            ("ขอบคุณนะ", "Gratitude"),
        ]
        
        for msg, desc in test_cases:
            print(f"\n📝 {desc}")
            print(f"   Input: '{msg}'")
            
            session = UserSession(user_id="test_user")
            
            result = await orchestrator.process_message(
                user_id="test_user",
                message=msg,
                session=session
            )
            
            print(f"   📤 Response Type: {result['type']}")
            print(f"   🎭 Persona: {result['persona']}")
            print(f"   🎯 Intent: {result.get('intent', 'unknown')}")
            print(f"   💬 Content: {result['content'][:60]}...")
            
            if result.get('crisis_alert'):
                print(f"   🚨 CRISIS ALERT TRIGGERED!")
    
    asyncio.run(run())


def example_2_workflow_context():
    """Example 2: Understanding WorkflowContext"""
    print("\n" + "=" * 70)
    print("Example 2: Workflow Context")
    print("=" * 70)
    
    context = WorkflowContext(
        user_id="Uxxx123",
        message="วันนี้รู้สึกนอยๆ",
        sentiment_score=-0.6,
        sentiment_label="NEGATIVE",
        primary_intent="emotional_support",
        intent_confidence=0.85,
        emotions=["sad", "tired"],
        crisis_level="NONE",
        is_crisis=False,
        r_score=45.0,
        recommended_persona=2,
        recommended_circle=1
    )
    
    print("\n📋 Workflow Context Fields:")
    print(f"   User ID: {context.user_id}")
    print(f"   Message: {context.message}")
    print(f"   Sentiment: {context.sentiment_label} ({context.sentiment_score})")
    print(f"   Intent: {context.primary_intent}")
    print(f"   Emotions: {context.emotions}")
    print(f"   Crisis Level: {context.crisis_level}")
    print(f"   R-Score: {context.r_score}")
    print(f"   Recommended Persona: {context.recommended_persona}")
    print(f"   Circle: {context.recommended_circle}")


def example_3_intent_routing():
    """Example 3: Intent Routing"""
    print("\n" + "=" * 70)
    print("Example 3: Intent Routing")
    print("=" * 70)
    
    intent_examples = {
        "greeting": ["สวัสดี", "หวัดดี", "ดีจ้า"],
        "emotional_support": ["นอยๆ", "เหนื่อย", "เศร้า"],
        "bible_question": ["ยอห์น 3:16", "พระคัมภีร์บอกว่า"],
        "request_video": ["ขอคลิป", "อยากดูวิดีโอ"],
        "small_talk": ["เป็นไงบ้าง", "ทำอะไรอยู่"],
    }
    
    async def run():
        orchestrator = MainOrchestrator()
        
        print("\n🗺️ Intent → Handler Mapping:")
        for intent_type, examples in intent_examples.items():
            print(f"\n   📌 {intent_type}:")
            for example in examples:
                session = UserSession(user_id="test_user")
                result = await orchestrator.process_message(
                    user_id="test_user",
                    message=example,
                    session=session
                )
                print(f"      '{example}' → Persona {result['persona']}")
    
    asyncio.run(run())


def example_4_crisis_handling():
    """Example 4: Crisis Detection and Handling"""
    print("\n" + "=" * 70)
    print("Example 4: Crisis Handling")
    print("=" * 70)
    
    async def run():
        orchestrator = MainOrchestrator()
        
        crisis_messages = [
            ("อยากตาย ไม่อยากอยู่แล้ว", "CRITICAL"),
            ("ไม่ไหวแล้ว มืดแปดด้าน", "CRITICAL"),
            ("วันนี้เหนื่อยมาก", "NORMAL"),
            ("รู้สึกไม่มีค่า", "WARNING"),
        ]
        
        print("\n🚨 Crisis Detection Test:")
        for msg, expected in crisis_messages:
            session = UserSession(user_id="test_user")
            result = await orchestrator.process_message(
                user_id="test_user",
                message=msg,
                session=session
            )
            
            is_crisis = result.get('crisis_alert', False)
            persona = result['persona']
            
            status = "🚨" if is_crisis else "✅"
            print(f"\n   {status} '{msg}'")
            print(f"      Crisis Alert: {is_crisis}")
            print(f"      Persona: {persona} {'(SOS)' if persona == 8 else ''}")
            
            if is_crisis:
                print(f"      Emergency contacts included: Yes")
    
    asyncio.run(run())


def example_5_middleware_integration():
    """Example 5: Middleware Integration"""
    print("\n" + "=" * 70)
    print("Example 5: Middleware Integration")
    print("=" * 70)
    
    async def mock_video_service(query: str) -> dict:
        """Mock video middleware"""
        print(f"   📡 Calling video middleware with: '{query}'")
        return {
            "url": f"https://cdn.example.com/video_{hash(query) % 1000}.mp4",
            "title": "คลิปหนุนใจสำหรับคุณ",
            "duration": "05:30"
        }
    
    async def run():
        orchestrator = MainOrchestrator()
        
        # Set middleware callback
        orchestrator.set_video_callback(mock_video_service)
        
        session = UserSession(user_id="test_user")
        result = await orchestrator.process_message(
            user_id="test_user",
            message="ขอคลิปหนุนใจ",
            session=session
        )
        
        print(f"\n   📤 Response Type: {result['type']}")
        print(f"   🎭 Persona: {result['persona']}")
    
    asyncio.run(run())


def example_6_session_updates():
    """Example 6: Session Updates"""
    print("\n" + "=" * 70)
    print("Example 6: Session Updates")
    print("=" * 70)
    
    async def run():
        orchestrator = MainOrchestrator()
        
        session = UserSession(user_id="test_user")
        print("\n📊 Session Before:")
        print(f"   Persona: {session.current_persona}")
        print(f"   Circle: {session.current_circle}")
        print(f"   R-Score: {session.r_score}")
        print(f"   Messages: {session.message_count}")
        
        # Process message
        result = await orchestrator.process_message(
            user_id="test_user",
            message="วันนี้รู้สึกนอยๆ",
            session=session
        )
        
        print("\n📊 Session After:")
        print(f"   Persona: {session.current_persona} (updated)")
        print(f"   Circle: {session.current_circle} (updated)")
        print(f"   R-Score: {session.r_score} (updated)")
        print(f"   Messages: {session.message_count}")
        print(f"   History: {len(session.conversation_history)} items")
    
    asyncio.run(run())


def example_7_configuration():
    """Example 7: Configuration Options"""
    print("\n" + "=" * 70)
    print("Example 7: Configuration")
    print("=" * 70)
    
    config = OrchestratorConfig(
        middleware_video_url="http://middleware:8000/api/video",
        middleware_quiz_url="http://middleware:8000/api/quiz",
        knowledge_base_url="http://kb:8001",
        maac_api_url="http://maac:8000/api",
        r_score_low_threshold=40.0,
        r_score_high_threshold=80.0,
        video_request_timeout=30
    )
    
    print("\n⚙️ Orchestrator Configuration:")
    print(f"   Video URL: {config.middleware_video_url}")
    print(f"   Quiz URL: {config.middleware_quiz_url}")
    print(f"   Knowledge Base: {config.knowledge_base_url}")
    print(f"   MAAC API: {config.maac_api_url}")
    print(f"   R-Score Low Threshold: {config.r_score_low_threshold}")
    print(f"   R-Score High Threshold: {config.r_score_high_threshold}")
    print(f"   Video Timeout: {config.video_request_timeout}s")


def example_8_full_integration():
    """Example 8: Full System Integration Flow"""
    print("\n" + "=" * 70)
    print("Example 8: Full Integration Flow")
    print("=" * 70)
    
    print("""
🔄 Complete Message Flow:

1️⃣  User: "วันนี้รู้สึกนอยๆ ตั้งแต่เช้า"
    ↓
2️⃣  LINE Gateway (Module 4)
    - Receive webhook
    - Parse message
    - Get UserSession from Redis
    ↓
3️⃣  Main Orchestrator (Module 3)
    - Step 1: NLP Analysis (Module 2)
      * Sentiment: NEGATIVE (-0.6)
      * Intent: emotional_support
      * Emotions: [sad, tired]
      * R-Score: 45
    - Step 2: Crisis Check
      * is_crisis: False
    - Step 3: Route Intent
      * Handler: _handle_emotional_support
    - Step 4: Search Knowledge (Module 1)
      * Query: "นอยๆ เศร้า กำลังใจ"
      * Results: [video_id: 123, ...]
    - Step 5: Build Response
      * Persona: 2 (Healing)
      * Type: flex (video card)
    ↓
4️⃣  LINE Gateway (Module 4)
    - Update session (persona=2, r_score=45)
    - Send Flex Message to LINE API
    ↓
5️⃣  User receives:
    💬 "อุ่นใจเข้าใจความรู้สึกของคุณพี่ค่ะ 💙
       พระเจ้าทรงเป็นที่ลี้ภัยของเรา..."
    
    [Video Card: การรักตัวเองตามพระคัมภีร์]
    
    [Quick Reply: ดูคลิปอื่น | ทำควิซ | คุยต่อ]
    
    — เพื่อนสาวสายเยียวยา 💙
    """)


def example_9_health_check():
    """Example 9: Health Check"""
    print("\n" + "=" * 70)
    print("Example 9: Health Check")
    print("=" * 70)
    
    orchestrator = MainOrchestrator()
    health = orchestrator.get_health()
    
    print("\n🏥 Orchestrator Health:")
    print(f"   Status: {health['status']}")
    print(f"   Timestamp: {health['timestamp']}")
    print("\n   Components:")
    for name, status in health['components'].items():
        icon = "✅" if status == "active" else "⚠️"
        print(f"   {icon} {name}: {status}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎛️ Module 3: Main Orchestrator - Examples")
    print("=" * 70)
    
    try:
        example_1_basic_usage()
        example_2_workflow_context()
        example_3_intent_routing()
        example_4_crisis_handling()
        example_5_middleware_integration()
        example_6_session_updates()
        example_7_configuration()
        example_8_full_integration()
        example_9_health_check()
        
        print("\n" + "=" * 70)
        print("✅ All examples completed!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
