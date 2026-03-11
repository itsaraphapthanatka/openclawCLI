#!/usr/bin/env python3
"""
Example usage of Module 2: NLP Processor
Nong Unjai AI System

This script demonstrates:
1. Basic sentiment analysis
2. Intent classification
3. Crisis detection
4. R-score calculation
5. Persona recommendation
6. Batch processing
"""

from module_2_nlp_processor import (
    NLPProcessor,
    ThaiTextProcessor,
    CrisisDetector,
    SentimentAnalyzer,
    IntentClassifier
)


def example_1_basic_analysis():
    """Example 1: Basic NLP Analysis"""
    print("=" * 70)
    print("Example 1: Basic NLP Analysis")
    print("=" * 70)
    
    processor = NLPProcessor()
    
    test_messages = [
        "สวัสดีค่ะ น้องอุ่นใจ",
        "วันนี้รู้สึกนอยๆ ตั้งแต่เช้าเลย",
        "พระเจ้ามีจริงปะ? สงสัยจัง",
        "ขอคลิปหนุนใจเรื่องการให้อภัยหน่อย",
    ]
    
    for msg in test_messages:
        result = processor.analyze(msg)
        
        print(f"\n📝 Input: {msg}")
        print(f"   Cleaned: {result.cleaned_text}")
        print(f"   Sentiment: {result.sentiment.label.name} ({result.sentiment.score:+.2f})")
        print(f"   Intent: {result.intent.primary_intent.value}")
        print(f"   Emotions: {', '.join(result.sentiment.emotions) if result.sentiment.emotions else 'None'}")
        print(f"   R-Score: {result.r_score:.1f}/100")
        print(f"   Persona: {result.recommended_persona}")
        print(f"   Circle: {result.recommended_circle}")
        print(f"   Time: {result.processing_time_ms}ms")


def example_2_crisis_detection():
    """Example 2: Crisis Detection (SOSVE Protocol)"""
    print("\n" + "=" * 70)
    print("Example 2: Crisis Detection (SOSVE)")
    print("=" * 70)
    
    processor = NLPProcessor()
    
    crisis_messages = [
        "อยากตาย ไม่อยากอยู่แล้ว",
        "ไม่ไหวแล้ว มืดแปดด้าน",
        "ไม่เหลืออะไรแล้ว ไร้ค่า",
        "ขอโทษทุกคน ดูแลตัวเองด้วยนะ",
        "วันนี้เหนื่อยมาก แต่ยังไหวอยู่",  # Not crisis
    ]
    
    for msg in crisis_messages:
        result = processor.analyze(msg)
        
        print(f"\n📝 Input: {msg}")
        print(f"   Crisis Level: {result.crisis.level.name}")
        
        if result.crisis.is_crisis:
            print(f"   🚨 ALERT: Crisis detected!")
            print(f"   Trigger Keywords: {result.crisis.trigger_keywords}")
            print(f"   Should Alert Human: {result.crisis.should_alert_human}")
            print(f"   Action: {result.crisis.recommended_action}")
            print(f"   → Use Persona 8 (SOS)")
        else:
            print(f"   ✅ No crisis detected")


def example_3_thai_processing():
    """Example 3: Thai Text Processing"""
    print("\n" + "=" * 70)
    print("Example 3: Thai Text Processing")
    print("=" * 70)
    
    processor = ThaiTextProcessor()
    
    test_texts = [
        "นอยยย มากกก ค่ะ",
        "ยม จัง เลย",
        "หวัดดี น้องอุ่นใจ สบายดีมั้ย",
        "https://example.com มาดูนี่สิ @bot",
    ]
    
    print("\n📋 Text Cleaning:")
    for text in test_texts:
        cleaned = processor.clean_text(text)
        print(f"   {text:40} → {cleaned}")
    
    print("\n🎭 Emotion Extraction:")
    emotion_texts = [
        "วันนี้เศร้า โกรธแฟนมาก",
        "กังวลเรื่องงาน เครียดสุดๆ",
        "มีความสุข ยิ้มทั้งวัน",
        "เหนื่อย ง่วง หิวข้าว",
    ]
    
    for text in emotion_texts:
        emotions = processor.extract_emotion_words(text)
        print(f"   {text:40} → {emotions}")


def example_4_intent_classification():
    """Example 4: Intent Classification"""
    print("\n" + "=" * 70)
    print("Example 4: Intent Classification")
    print("=" * 70)
    
    processor = NLPProcessor()
    
    intent_examples = {
        "GREETING": ["สวัสดี", "หวัดดี", "ดีค่ะ", "hi"],
        "BIBLE_QUESTION": ["ยอห์น 3:16 ว่าอะไร", "พระคัมภีร์บอกว่า"],
        "EMOTIONAL_SUPPORT": ["นอยๆ", "เหนื่อยจัง", "เศร้า"],
        "REQUEST_VIDEO": ["ขอคลิปหน่อย", "อยากดูวิดีโอ"],
        "QUIZ_ANSWER": ["ตอบ A", "ข้อ 2", "เลือก B"],
        "GRATITUDE": ["ขอบคุณนะ", "thanks", "ดีมาก"],
    }
    
    for intent_type, examples in intent_examples.items():
        print(f"\n📌 {intent_type}:")
        for example in examples:
            result = processor.analyze(example)
            confidence = result.intent.confidence
            print(f"   '{example}' → {result.intent.primary_intent.value} ({confidence:.2f})")


def example_5_r_score_calculation():
    """Example 5: R-Score Calculation"""
    print("\n" + "=" * 70)
    print("Example 5: R-Score Calculation")
    print("=" * 70)
    
    from module_2_nlp_processor import RScoreComponents
    
    print("\n📊 R-Score Formula: R = (S×0.4) + (Q×0.3) + (I×0.3)")
    print()
    
    examples = [
        # (S, Q, I, description)
        (20, 30, 40, "New user, feeling down"),
        (60, 70, 80, "Regular user, doing well"),
        (80, 90, 85, "Active user, ready to help others"),
        (10, 20, 15, "Crisis situation, needs help"),
    ]
    
    for s, q, i, desc in examples:
        components = RScoreComponents(
            sentiment_score=s,
            quiz_performance=q,
            interaction_frequency=i
        )
        r_score = components.calculate()
        
        print(f"   {desc}")
        print(f"   S={s}, Q={q}, I={i} → R-Score = {r_score:.1f}")
        
        if r_score < 40:
            level = "⚠️  Needs support (Circle 1)"
        elif r_score < 60:
            level = "📈  Developing (Circle 1-2)"
        elif r_score < 80:
            level = "✅  Doing well (Circle 2-3)"
        else:
            level = "🌟  Ready to help others (Circle 3)"
        
        print(f"   {level}")
        print()


def example_6_persona_recommendation():
    """Example 6: Persona Recommendation"""
    print("\n" + "=" * 70)
    print("Example 6: Persona Recommendation")
    print("=" * 70)
    
    processor = NLPProcessor()
    
    persona_examples = [
        ("พระเจ้ามีจริงปะ? อยากรู้", "Theology question"),
        ("นอยๆ วันนี้", "Emotional support"),
        ("อยากตาย ไม่อยากอยู่", "Crisis"),
        ("สวัสดีค่ะ", "Greeting"),
        ("ขอคลิปหนุนใจ", "Request video"),
        ("เทสตอบ A", "Quiz answer"),
    ]
    
    persona_names = {
        1: "พี่สาวสายปัญญา (Intellectual)",
        2: "เพื่อนสาวสายเยียวยา (Healing)",
        3: "น้องสาวสายกิจกรรม (Social)",
        8: "หน่วยกู้ใจสายด่วน (SOS)",
        6: "น้องอุ่นใจสายห่วงใย (Watcher)",
        11: "น้องน้อยสายเก็บแต้ม (Gamer)",
    }
    
    print()
    for msg, desc in persona_examples:
        result = processor.analyze(msg)
        persona_name = persona_names.get(result.recommended_persona, f"Persona {result.recommended_persona}")
        
        print(f"   '{msg}'")
        print(f"   → {persona_name} (Circle {result.recommended_circle})")
        print(f"     [{desc}]")
        print()


def example_7_batch_processing():
    """Example 7: Batch Processing"""
    print("\n" + "=" * 70)
    print("Example 7: Batch Processing")
    print("=" * 70)
    
    processor = NLPProcessor()
    
    messages = [
        "สวัสดีค่ะ",
        "วันนี้รู้สึกยังไง",
        "นอยๆ อ่ะ",
        "พระคัมภีร์ข้อไหนพูดถึงความรัก",
    ]
    
    print(f"\n📨 Processing {len(messages)} messages...")
    results = processor.batch_analyze(messages)
    
    for msg, result in zip(messages, results):
        print(f"\n   '{msg}'")
        print(f"   → Sentiment: {result.sentiment.label.name}")
        print(f"   → Intent: {result.intent.primary_intent.value}")
        print(f"   → Persona: {result.recommended_persona}")


def example_8_health_check():
    """Example 8: System Health Check"""
    print("\n" + "=" * 70)
    print("Example 8: System Health Check")
    print("=" * 70)
    
    processor = NLPProcessor()
    health = processor.get_health()
    
    print("\n🏥 System Health:")
    print(f"   Status: {health['status']}")
    print(f"   GPU Available: {health['gpu_available']}")
    print(f"   Model: {health['model']}")
    
    print("\n   Components:")
    for component, status in health['components'].items():
        icon = "✅" if status == "active" else "⚠️"
        print(f"   {icon} {component}: {status}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧠 Module 2: NLP Processor - Examples")
    print("=" * 70)
    
    try:
        example_1_basic_analysis()
        example_2_crisis_detection()
        example_3_thai_processing()
        example_4_intent_classification()
        example_5_r_score_calculation()
        example_6_persona_recommendation()
        example_7_batch_processing()
        example_8_health_check()
        
        print("\n" + "=" * 70)
        print("✅ All examples completed!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
