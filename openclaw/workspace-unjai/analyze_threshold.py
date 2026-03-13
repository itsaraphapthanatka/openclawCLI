#!/usr/bin/env python3
"""
Fix: Lower Pinecone score threshold
เหตุผล: คะแนนค้นหาอยู่ที่ ~0.10-0.14 แต่ threshold ตั้งไว้ที่ 0.70
ทำให้ไม่มีผลลัพธ์ที่ผ่านการกรอง
"""

print("="*70)
print("🔧 Analysis: Why LINE says 'not in Pinecone'")
print("="*70)

print("""
📊 ผลการทดสอบค้นหา:
   Query "ตรุษจีน":
     - Found 3 matches
     - Score: 0.102 (ต่ำมาก!)
   
   Query "ความรัก":
     - Found 3 matches
     - Score: 0.138

⚠️  ปัญหา: คะแนนต่ำเกินไป!
   - ผลลัพธ์ที่เจอมี score ~0.10-0.14
   - แต่ในโค้ดกำหนด min_score = 0.70
   - ผล: ถูกกรองออกหมด → ไม่มี video ส่งกลับไป LINE

🔧 แก้ไข: ลด threshold จาก 0.70 → 0.08
""")

# Show the fix
print("="*70)
print("📝 การแก้ไขในโค้ด:")
print("="*70)
print("""
ไฟล์: modules/line_orchestrator.py

เดิม (บรรทัด ~80):
    async def search_pinecone(self, 
                             query_embedding: List[float],
                             top_k: int = 3,
                             min_score: float = 0.70,  ← สูงเกินไป!
                             filter: Optional[Dict[str, Any]] = None) -> List[Dict]:

แก้เป็น:
    async def search_pinecone(self, 
                             query_embedding: List[float],
                             top_k: int = 3,
                             min_score: float = 0.08,   ← ลดลงให้เหมาะสม
                             filter: Optional[Dict[str, Any]] = None) -> List[Dict]:

และใน search_pinecone_by_text:
    results = await self.search_pinecone(embedding, top_k=top_k, min_score=0.08)
""")

print("="*70)
print("✅ อธิบาย:")
print("="*70)
print("""
คะแนน (Score) คือ cosine similarity ระหว่าง embedding ของคำค้นหา
กับ embedding ของคลิปวิดีโอ

- 1.0 = ตรงกันที่สุด
- 0.5 = คล้ายกันปานกลาง  
- 0.1 = ตรงกันบ้าง (แต่ยังพอใช้ได้)

การใช้ threshold 0.70 อาจเหมาะกับข้อมูลบางชนิด
แต่สำหรับ video transcripts ที่มีความหลากหลาย
ควรใช้ threshold ต่ำกว่า (~0.05-0.10) เพื่อให้เจอผลลัพธ์

หลังแก้ไขแล้ว ต้องรีบิลด์ container ใหม่ค่ะ
""")
