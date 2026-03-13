"""
Working Example: LINE + Pinecone Integration
ตัวอย่างการใช้งานจริงที่เชื่อมต่อกับ Pinecone ได้เลย
"""

import os
import sys
sys.path.insert(0, '/home/node/.openclaw/workspace-unjai')

from modules.pinecone_connector import get_connector, PineconeVideoResult

print("=" * 70)
print("🚀 ทดสอบการเชื่อมต่อ Pinecone จริง")
print("=" * 70)

# 1. เริ่มต้น Connector
print("\n📡 1. กำลังเชื่อมต่อ Pinecone...")
connector = get_connector()
print("✅ เชื่อมต่อสำเร็จ!")

# 2. ดึงตัวอย่าง Records
print("\n📹 2. กำลังดึงตัวอย่างวิดีโอจาก Pinecone...")
samples = connector.get_sample_records(3)

if samples:
    print(f"✅ พบ {len(samples)} วิดีโอ:")
    for i, video in enumerate(samples, 1):
        print(f"\n   🎬 วิดีโอ #{i}")
        print(f"      Score: {video.score:.3f}")
        print(f"      Clip URL: {video.clip_url}")
        print(f"      YouTube: {video.video_url}")
        print(f"      Time: {video.start_time}s - {video.end_time}s")
        print(f"      Transcript: {video.transcript[:60]}...")
else:
    print("⚠️ ไม่พบวิดีโอ (อาจยังไม่มีข้อมูลใน Pinecone)")

# 3. ทดสอบค้นหาด้วยข้อความ
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    print("\n🔎 3. ทดสอบค้นหาด้วยข้อความ 'การให้อภัย'...")
    
    results = connector.search_by_text(
        text="การให้อภัย",
        top_k=3,
        min_score=0.70
    )
    
    if results:
        print(f"✅ พบ {len(results)} วิดีโอที่ตรงกับ 'การให้อภัย':")
        for video in results:
            print(f"\n   🎯 Score: {video.score:.3f}")
            print(f"      Clip: {video.clip_url}")
            print(f"      Reason: {video.reason[:50]}...")
    else:
        print("ℹ️ ไม่พบวิดีโอที่ตรง (อาจต้องปรับ min_score หรือเพิ่มข้อมูล)")
else:
    print("\n⏭️ 3. ข้ามการทดสอบค้นหาด้วยข้อความ (ไม่มี OPENAI_API_KEY)")

print("\n" + "=" * 70)
print("✅ ทดสอบเสร็จสิ้น")
print("=" * 70)
print("\n💡 วิธีใช้งานใน LINE Gateway:")
print("""
   from modules.pinecone_connector import get_connector
   
   connector = get_connector()
   videos = connector.search_by_text(
       text=user_message,
       top_k=3,
       min_score=0.70
   )
   
   if videos:
       # ส่งวิดีโอกลับไปใน LINE
       for video in videos:
           send_video_message(video.clip_url)
""")
