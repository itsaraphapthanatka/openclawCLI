#!/usr/bin/env python3
"""
Example usage of Module 1: The Brain
Nong Unjai AI System

This script demonstrates how to:
1. Initialize the knowledge base
2. Add videos with 3 Circles classification
3. Search for relevant content
4. Get personalized recommendations
"""

import os
from datetime import datetime

# Set environment variables for testing (replace with your actual keys)
os.environ.setdefault("OPENAI_API_KEY", "sk-your-key-here")
os.environ.setdefault("PINECONE_API_KEY", "your-pinecone-key")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_DB", "nong_unjai")
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "password")

from module_1_the_brain import (
    KnowledgeBase,
    VideoMetadata,
    CircleLevel,
    extract_scripture_references,
    chunk_transcript
)


def example_1_add_videos():
    """Example: Add videos to knowledge base"""
    print("=" * 60)
    print("Example 1: Adding Videos to Knowledge Base")
    print("=" * 60)
    
    kb = KnowledgeBase()
    
    # Video 1: Circle 1 - Self (การรักตัวเอง)
    video1 = VideoMetadata(
        video_id="demo_self_001",
        youtube_url="https://youtube.com/watch?v=self001",
        title="เห็นคุณค่าในตัวเองตามพระคัมภีร์",
        description="คำสอนเกี่ยวกับการรักตัวเองและเห็นคุณค่า",
        transcript="""
        วันนี้เรามาคุยกันเรื่องการรักตัวเอง หลายคนรู้สึกว่าตัวเองไม่มีค่า
        แต่พระคัมภีร์บอกเราว่า พระเจ้าทรงสร้างเราตามพระฉายของพระองค์
        ปฐมกาล 1:27 บอกว่า พระเจ้าทรงสร้างมนุษย์ตามพระฉายของพระองค์
        นั่นหมายความว่าเรามีคุณค่าในสายพระเนตรของพระองค์
        ไม่ว่าเราจะผิดพลาดแค่ไหน พระเจ้ายังทรงรักเรา
        """,
        summary="คำสอนเรื่อง self-worth และการเห็นคุณค่าในตัวเองจากพระคัมภีร์",
        duration_seconds=900,
        circle_level=CircleLevel.SELF,
        topic_tags=["self-love", "identity", "self-worth", "healing"],
        scripture_refs=[
            {"book": "Genesis", "thai_book": "ปฐมกาล", "chapter": 1, "verse": "27"}
        ],
        tone="gentle",
        pastor_name="Pastor Somchai",
        language="th"
    )
    
    # Video 2: Circle 2 - Close Ones (ความสัมพันธ์)
    video2 = VideoMetadata(
        video_id="demo_relationship_001",
        youtube_url="https://youtube.com/watch?v=rel001",
        title="การให้อภัยในครอบครัว",
        description="เรียนรู้ที่จะให้อภัยคนในครอบครัว",
        transcript="""
        ความสัมพันธ์ในครอบครัวเป็นสิ่งที่ละเอียดอ่อน บางครั้งเราถูกทำร้าย
        โดยคนที่เรารัก แต่พระคัมภีร์สอนเราว่า จงให้อภัยกัน
        เอเฟซัส 4:32 บอกว่า จงมีน้ำใจอ่อนโยนกัน และให้อภัยกัน
        เหมือนอย่างที่พระเจ้าทรงให้อภัยพวกท่านในเยซูคริสต์
        การให้อภัยไม่ได้แปลว่ายอมรับความผิด แต่เป็นการปล่อยวางความเจ็บปวด
        """,
        summary="คำสอนเรื่องการให้อภัยและการสมานความสัมพันธ์ในครอบครัว",
        duration_seconds=720,
        circle_level=CircleLevel.CLOSE_ONES,
        topic_tags=["forgiveness", "family", "relationship", "healing"],
        scripture_refs=[
            {"book": "Ephesians", "thai_book": "เอเฟซัส", "chapter": 4, "verse": "32"}
        ],
        tone="comforting",
        pastor_name="Pastor Malee",
        language="th"
    )
    
    # Video 3: Circle 3 - Society (การช่วยเหลือสังคม)
    video3 = VideoMetadata(
        video_id="demo_society_001",
        youtube_url="https://youtube.com/watch?v=soc001",
        title="การเป็นพรให้สังคม",
        description="เรียกร้องให้คริสเตียนออกไปช่วยเหลือสังคม",
        transcript="""
        ในฐานะคริสเตียน เราไม่ได้ถูกเรียกให้อยู่แต่ในคริสตจักร
        แต่เราถูกเรียกให้ออกไปเป็นพรให้กับสังคม
        กาลาเทีย 6:9-10 บอกว่า อย่าให้เราเหนื่อยหน่ายในการทำความดี
        เพราะถ้าเราไม่ย่อท้อ เราจะได้เก็บเกี่ยวในคราวเดียวกัน
        การช่วยเหลือผู้อื่นไม่ใช่แค่การให้เงิน แต่เป็นการให้เวลา ให้กำลังใจ
        ให้ความรักกับคนที่ต้องการ
        """,
        summary="แรงบันดาลใจในการออกไปช่วยเหลือสังคมและชุมชน",
        duration_seconds=600,
        circle_level=CircleLevel.SOCIETY,
        topic_tags=["volunteering", "community", "social-impact", "calling"],
        scripture_refs=[
            {"book": "Galatians", "thai_book": "กาลาเทีย", "chapter": 6, "verse": "9-10"}
        ],
        tone="energetic",
        pastor_name="Pastor John",
        language="th"
    )
    
    # Add videos
    videos = [video1, video2, video3]
    for video in videos:
        success = kb.add_video(video)
        status = "✅ Added" if success else "❌ Failed"
        print(f"{status}: {video.title} (Circle {video.circle_level.value})")
    
    print("\n✨ Videos added successfully!\n")


def example_2_search():
    """Example: Search for videos"""
    print("=" * 60)
    print("Example 2: Semantic Search")
    print("=" * 60)
    
    kb = KnowledgeBase()
    
    # Search queries simulating user emotions
    queries = [
        ("รู้สึกไม่มีค่า อยากได้กำลังใจ", CircleLevel.SELF),
        ("ทะเลาะกับแม่ อยากให้อภัย", CircleLevel.CLOSE_ONES),
        ("อยากช่วยคนอื่น แต่ไม่รู้จะเริ่มยังไง", CircleLevel.SOCIETY),
    ]
    
    for query, circle in queries:
        print(f"\n🔍 Query: '{query}'")
        print(f"   User Circle Level: {circle.name}")
        print("-" * 40)
        
        results = kb.search(query, user_circle_level=circle, top_k=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result.metadata.title}")
                print(f"      Score: {result.score:.3f}")
                print(f"      Circle: {result.metadata.circle_level.name}")
                print(f"      Tags: {', '.join(result.metadata.topic_tags)}")
        else:
            print("   No results found")
    
    print("\n")


def example_3_recommendations():
    """Example: Get personalized recommendations"""
    print("=" * 60)
    print("Example 3: Personalized Recommendations")
    print("=" * 60)
    
    kb = KnowledgeBase()
    
    moods = ["sad", "anxious", None]
    
    for mood in moods:
        mood_str = mood or "neutral"
        print(f"\n💭 Mood: {mood_str}")
        print(f"   Circle Level: SELF")
        print("-" * 40)
        
        recommendations = kb.get_recommendations(
            user_circle_level=CircleLevel.SELF,
            watched_videos=["demo_self_001"],  # Already watched
            mood=mood
        )
        
        if recommendations:
            for rec in recommendations:
                print(f"   📹 {rec.metadata.title}")
                print(f"      {rec.metadata.summary[:100]}...")
        else:
            print("   No recommendations available")
    
    print("\n")


def example_4_utilities():
    """Example: Utility functions"""
    print("=" * 60)
    print("Example 4: Utility Functions")
    print("=" * 60)
    
    # Extract scripture references
    text = """
    วันนี้เราจะมาศึกษายอห์น 3:16 ซึ่งเป็นข้อพระคัมภีร์ที่มีความสำคัญมาก
    และสดุดี 23:1-6 ที่พูดถึงพระเจ้าทรงเป็นผู้เลี้ยงแกะของเรา
    นอกจากนี้ โรม 8:28 ก็บอกว่าพระเจ้าช่วยคนที่รักพระองค์ให้ได้รับประโยชน์
    """
    
    print("\n📖 Extracting Scripture References:")
    print(f"   Text: {text[:50]}...")
    print("-" * 40)
    
    refs = extract_scripture_references(text)
    for ref in refs:
        print(f"   • {ref['full_reference']} → {ref['book']} {ref['chapter']}:{ref['verse']}")
    
    # Chunk transcript
    long_transcript = """
    นี่คือข้อความยาวๆ ที่ต้องการแบ่งเป็นส่วนเล็กๆ เพื่อสร้าง embeddings
    แต่ละส่วนจะมีความยาวประมาณ 400 ตัวอักษร และทับซ้อนกัน 50 ตัวอักษร
    เพื่อให้ context ไม่ขาดตอนเมื่อแบ่งเป็นช่วงๆ
    """ * 5  # Make it longer
    
    print("\n✂️ Chunking Transcript:")
    print(f"   Original length: {len(long_transcript)} chars")
    print("-" * 40)
    
    chunks = chunk_transcript(long_transcript, chunk_size=400, overlap=50)
    print(f"   Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"   Chunk {i}: {chunk['char_count']} chars")
    if len(chunks) > 3:
        print(f"   ... and {len(chunks) - 3} more chunks")
    
    print("\n")


def example_5_stats():
    """Example: Get knowledge base stats"""
    print("=" * 60)
    print("Example 5: Knowledge Base Statistics")
    print("=" * 60)
    
    kb = KnowledgeBase()
    stats = kb.get_stats()
    
    print("\n📊 Stats:")
    print(f"   Vector DB: {stats.get('vector_db', {})}")
    print(f"   Cache Status: {stats.get('cache_status', 'unknown')}")
    print("\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧠 Module 1: The Brain - Examples")
    print("=" * 60 + "\n")
    
    try:
        # Run examples
        example_5_stats()      # Check stats first
        example_1_add_videos() # Add sample videos
        example_2_search()     # Search
        example_3_recommendations()  # Get recommendations
        example_4_utilities()  # Utility functions
        
        print("=" * 60)
        print("✅ All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure you have set the correct API keys in environment variables.")
