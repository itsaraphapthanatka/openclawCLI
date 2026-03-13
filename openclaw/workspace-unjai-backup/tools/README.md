# 🔍 Search Specialist Auto-Tool v2.0

## ภาพรวม

Tool นี้ช่วยให้ Search Specialist Agent ทำงานอัตโนมัติตาม **AGENTS.md** อย่างเคร่งครัด

**Role:** นักสืบค้นหาความหมาย (Parallel Retriever)

## 🎯 ความสอดคล้อง AGENTS.md

### ✅ Task: Hybrid Parallel Search
```
ในทุกครั้งที่มีคำถามเข้ามา ต้องรันระบบค้นหาแบบคู่ขนาน (Hybrid Search) เสมอ:
├── 🔍 ค้นหา Text จาก MEMORY.md (ฐานคำตอบหลัก)
└── 🔍 ค้นหา Vector จาก Pinecone (Namespace: highlights) เพื่อหาคลิปที่เกี่ยวข้อง
```

### 🚨 กฎเหล็ก (Iron Rule)
```
แม้จะเจอคำตอบใน Text แล้ว 
แต่หากพบวิดีโอที่มี Similarity Score > 0.80
ห้ามทิ้ง! ต้องส่ง Metadata (URL, Quiz, Reason) แนบไปกับชุดคำตอบเสมอ
เพื่อให้ Journey Architect ตัดสินใจป้ายยา
```

## โครงสร้างไฟล์

```
tools/
├── search_specialist_tool.json    # คอนฟิกูเรชั่น v2.0
├── search_specialist_tool.py      # โค้ด Hybrid Search
└── README.md                      # เอกสารนี้
```

## การทำงาน

### 1. Hybrid Parallel Search

```python
result = tool.hybrid_search("ตรุษจีน")

# ผลลัพธ์:
{
  "text_results": [...],           # จาก MEMORY.md
  "video_results": [...],          # จาก Pinecone
  "high_priority_videos": [...],   # Score > 0.80 (กฎเหล็ก!)
  "has_high_priority": True,
  "iron_rule_applied": True,
  "metadata_for_journey_architect": {...}
}
```

### 2. Iron Rule Enforcement

```python
IRON_RULE_THRESHOLD = 0.80

# ถ้า video มี score > 0.80
if video["score"] > 0.80:
    video["high_priority"] = True
    # ต้องส่ง metadata นี้ไปกับคำตอบเสมอ!
```

### 3. Data Flow

```
User Query
    ↓
┌─────────────────────────────────────────┐
│  Search Specialist (Hybrid Search)      │
│  ├── Parallel Task 1: MEMORY.md         │
│  └── Parallel Task 2: Pinecone          │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Iron Rule Check                        │
│  ├── Score > 0.80? → High Priority! 🚨  │
│  └── Mark for Journey Architect         │
└─────────────────────────────────────────┘
    ↓
Journey Architect (ตัดสินใจป้ายยา)
    ↓
Front-Desk (ส่งคำตอบ)
    ↓
LINE Response
```

## การใช้งาน

### 1. รีบิลด์ระบบ

```bash
cd /home/node/.openclaw/workspace-unjai/docker
./rebuild_hybrid.sh
```

### 2. ทดสอบใน LINE

พิมพ์:
- `"ตรุษจีน"`
- `"ความรัก"`
- `"การให้อภัย"`

### 3. ดู Logs

```bash
docker-compose logs -f line-gateway | grep -E 'Hybrid|Iron|Score|video'
```

## ผลลัพธ์ที่คาดหวัง

```
🔍 HYBRID PARALLEL SEARCH: "ตรุษจีน"
📚 [1/2] Searching MEMORY.md...
    ✅ Found 2 text results
🎬 [2/2] Searching Pinecone (highlights)...
    ✅ Found 3 video results

🚨 IRON RULE CHECK:
    High priority videos (score > 0.80): 1
    ⚡ MUST SEND: https://nongaunjai.febradio.org/... (score: 0.823)

✅ HYBRID SEARCH COMPLETE
   Text: 2 | Videos: 3 | High Priority: 1

🎯 Journey Architect:
   🚨 IRON RULE APPLIED: High priority video detected
   → decision: video_package

🎙️ Front-Desk: Sending video with metadata
```

## การตั้งค่า

ใน `docker/.env`:

```env
# OpenAI (สำหรับ embeddings)
OPENAI_API_KEY=sk-...

# Pinecone
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_HOST=https://aunjai-knowledge-3ygam8j.svc.aped-4627-b74a.pinecone.io
PINECONE_NAMESPACE=highlights

# Base URL (สำหรับเติมใน clip_url)
BASE_URL=https://nongaunjai.febradio.org
```

## ฟังก์ชั่นหลัก

### `hybrid_search(query)`
ค้นหาแบบคู่ขนาน (Text + Video)

### `search_memory_md(query)`
ค้นหาใน MEMORY.md

### `search_pinecone(embedding)`
ค้นหาใน Pinecone Vector DB

### `generate_embedding(text)`
สร้าง embedding vector (384 dimensions)

## ข้อมูลเพิ่มเติม

- **Version:** 2.0.0
- **AGENTS.md Compliance:** 100%
- **Iron Rule Threshold:** 0.80
- **Pinecone Dimension:** 384
- **Embedding Model:** text-embedding-3-small
