"""
LINE + Pinecone Integration - DEMO with Sample Data
แสดงตัวอย่างการทำงานจริงเมื่อมีข้อมูลใน Pinecone
"""

import os
import sys
from typing import List, Dict
from dataclasses import dataclass

sys.path.insert(0, '/home/node/.openclaw/workspace-unjai')


@dataclass
class DemoVideoResult:
    """Demo video result (simulating Pinecone data)"""
    id: str
    score: float
    clip_url: str
    video_url: str
    start_time: int
    end_time: int
    transcript: str
    reason: str
    type: str = "highlight"


class DemoPineconeConnector:
    """
    🔍 Demo Connector - จำลองข้อมูล Pinecone
    ใช้สำหรับทดสอบการทำงานก่อนมีข้อมูลจริง
    """
    
    # 🎬 ตัวอย่างวิดีโอ (simulating Pinecone data)
    # หมายเหตุ: ในระบบจริง clip_url จะถูกเติม Base URL นำหน้าโดยอัตโนมัติ
    BASE_URL = "https://nongaunjai.febradio.org"
    
    SAMPLE_VIDEOS = [
        DemoVideoResult(
            id="vid_001",
            score=0.85,
            clip_url=f"{BASE_URL}/static/clips/forgiveness_001_120_180.mp4",
            video_url="https://www.youtube.com/watch?v=abc123",
            start_time=120,
            end_time=180,
            transcript="การให้อภัยเป็นเรื่องยาก แต่พระเจ้าทรงสอนให้เราให้อภัยกัน...",
            reason="บทเรียนเรื่องการให้อภัยในครอบครัว"
        ),
        DemoVideoResult(
            id="vid_002",
            score=0.82,
            clip_url=f"{BASE_URL}/static/clips/healing_001_45_90.mp4",
            video_url="https://www.youtube.com/watch?v=def456",
            start_time=45,
            end_time=90,
            transcript="เมื่อเราเจ็บปวด พระเจ้าทรงเป็นที่ลี้ภัยของเรา...",
            reason="การเยียวยาใจเมื่อถูกทำร้าย"
        ),
        DemoVideoResult(
            id="vid_003",
            score=0.78,
            clip_url=f"{BASE_URL}/static/clips/work_stress_001_200_250.mp4",
            video_url="https://www.youtube.com/watch?v=ghi789",
            start_time=200,
            end_time=250,
            transcript="ในวันที่งานหนัก จงละความกระวนกระวายไว้กับพระองค์...",
            reason="รับมือกับความเครียดที่ทำงาน"
        ),
        DemoVideoResult(
            id="vid_004",
            score=0.91,
            clip_url=f"{BASE_URL}/static/clips/prayer_guide_001_10_60.mp4",
            video_url="https://www.youtube.com/watch?v=jkl012",
            start_time=10,
            end_time=60,
            transcript="วิธีอธิษฐานที่ถูกต้องคือการพูดคุยกับพระเจ้าด้วยความจริงใจ...",
            reason="คู่มือการอธิษฐานสำหรับผู้เริ่มต้น"
        ),
        DemoVideoResult(
            id="vid_005",
            score=0.75,
            clip_url=f"{BASE_URL}/static/clips/relationship_001_300_360.mp4",
            video_url="https://www.youtube.com/watch?v=mno345",
            start_time=300,
            end_time=360,
            transcript="ความรักในพระเจ้าสอนให้เรารักเพื่อนมนุษย์ด้วย...",
            reason="การสร้างความสัมพันธ์ที่ดี"
        )
    ]
    
    def __init__(self):
        print("🔍 Demo Pinecone Connector initialized")
        print(f"   📹 Loaded {len(self.SAMPLE_VIDEOS)} sample videos")
    
    def search_by_text(self, text: str, top_k: int = 3, min_score: float = 0.70) -> List[DemoVideoResult]:
        """
        🔍 ค้นหาวิดีโอตามข้อความ (simulated)
        
        ในระบบจริงจะใช้ OpenAI embedding + Pinecone vector search
        """
        print(f"\n🔎 Searching for: '{text}'")
        print(f"   Parameters: top_k={top_k}, min_score={min_score}")
        
        # 🎯 Simple keyword matching (simulating semantic search)
        text_lower = text.lower()
        
        # กำหนดคะแนนตาม keyword matching
        scored_videos = []
        for video in self.SAMPLE_VIDEOS:
            score = self._calculate_relevance(text_lower, video)
            if score >= min_score:
                # Create copy with adjusted score
                from copy import copy
                v = copy(video)
                v.score = score
                scored_videos.append(v)
        
        # เรียงตาม score และเลือก top_k
        scored_videos.sort(key=lambda x: x.score, reverse=True)
        results = scored_videos[:top_k]
        
        print(f"✅ Found {len(results)} matching videos")
        return results
    
    def _calculate_relevance(self, query: str, video: DemoVideoResult) -> float:
        """คำนวณความเกี่ยวข้อง (simulated semantic similarity)"""
        
        # คำสำคัญและวิดีโอที่เกี่ยวข้อง
        keyword_map = {
            "ให้อภัย": ["vid_001", "vid_002"],
            "เยียวยา": ["vid_002"],
            "เจ็บ": ["vid_002"],
            "เหนื่อย": ["vid_003"],
            "งาน": ["vid_003"],
            "เครียด": ["vid_003"],
            "อธิษฐาน": ["vid_004"],
            "สวด": ["vid_004"],
            "ความสัมพันธ์": ["vid_005"],
            "ครอบครัว": ["vid_001", "vid_005"],
            "รัก": ["vid_005"]
        }
        
        base_score = 0.0
        for keyword, video_ids in keyword_map.items():
            if keyword in query and video.id in video_ids:
                base_score = max(base_score, 0.75 + (0.15 * (query.count(keyword))))
        
        # ถ้าไม่ match keyword ใดเลย ให้ score ต่ำ
        if base_score == 0.0:
            base_score = 0.65  # Slight match
        
        # เพิ่ม random factor เล็กน้อย
        import random
        return min(0.95, base_score + random.uniform(-0.05, 0.05))


def demo_line_integration():
    """
    🚀 จำลองการทำงานใน LINE Gateway
    """
    print("=" * 70)
    print("🚀 DEMO: LINE + Pinecone Integration")
    print("=" * 70)
    
    # Initialize connector
    connector = DemoPineconeConnector()
    
    # ทดสอบหลายคำถาม
    test_queries = [
        "อยากรู้เรื่องการให้อภัยค่ะ",
        "เหนื่อยกับงานมากเลย",
        "สอนวิธีอธิษฐานหน่อย",
        "มีปัญหาครอบครัวค่ะ",
        "สวัสดี"  # ไม่มี keyword match
    ]
    
    print("\n" + "-" * 70)
    print("📝 ทดสอบการค้นหา:")
    print("-" * 70)
    
    for query in test_queries:
        results = connector.search_by_text(query, top_k=2, min_score=0.70)
        
        print(f"\n👤 User: \"{query}\"")
        
        if results:
            print(f"   🤖 Bot: พบ {len(results)} วิดีโอที่ตรงกับคำถาม!")
            for i, video in enumerate(results, 1):
                print(f"      {i}. 🎬 {video.reason}")
                print(f"         Score: {video.score:.2f}")
                print(f"         Clip: {video.clip_url}")
        else:
            print("   🤖 Bot: ตอบเป็นข้อความ (ไม่มีวิดีโอที่ตรง)")
    
    print("\n" + "=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)


def show_integration_code():
    """
    💻 แสดงโค้ดการใช้งานจริง
    """
    code = '''
# 📱 ใช้งานใน LINE Gateway (main.py)

from modules.pinecone_connector import get_connector
from modules.module_4_line_gateway import LineGateway

# Initialize
line_gateway = LineGateway()
pinecone = get_connector()

async def handle_user_message(user_id, message_text):
    """
    🔍 Search Specialist + Journey Architect
    """
    # 1. ค้นหาวิดีโอใน Pinecone
    videos = pinecone.search_by_text(
        text=message_text,
        top_k=3,
        min_score=0.70
    )
    
    # 2. Journey Architect: ตัดสินใจตาม 3-Filter System
    if videos and user_r_score >= 30:
        # ส่งวิดีโอ
        for video in videos:
            await line_gateway.send_video_message(
                user_id=user_id,
                video_url=video.clip_url,
                thumbnail=f"https://img.youtube.com/vi/{extract_id(video.video_url)}/0.jpg"
            )
    else:
        # ส่งข้อความ
        await line_gateway.send_text_message(
            user_id=user_id,
            text="คำตอบจาก MEMORY.md..."
        )
'''
    print(code)


if __name__ == "__main__":
    # Run demo
    demo_line_integration()
    
    print("\n💻 ตัวอย่างโค้ดการใช้งานจริง:")
    print("-" * 70)
    show_integration_code()
