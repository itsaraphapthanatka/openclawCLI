# Module 1: The Brain - Knowledge Base & Vector DB

## 📚 Overview

Module นี้เป็น **"สมอง"** ของระบบ Nong Unjai AI รับผิดชอบ:
- จัดการ Vector Database (Pinecone) สำหรับ semantic search
- เก็บ metadata วิดีโอใน PostgreSQL
- สร้าง embeddings จากข้อความ (OpenAI)
- จัดหมวดหมู่เนื้อหาตาม **3 Circles Logic**
- Caching ด้วย Redis

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Module 1: The Brain                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Embedding   │  │  Vector DB   │  │   Metadata   │      │
│  │  Generator   │→ │  (Pinecone)  │  │   Store      │      │
│  │  (OpenAI)    │  │              │  │ (PostgreSQL) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│                    ┌───────────────┐                        │
│                    │  KnowledgeBase │                        │
│                    │  (Main API)   │                        │
│                    └───────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🔧 Environment Variables

สร้างไฟล์ `.env` หรือ set environment variables:

```env
# OpenAI (สำหรับ Embeddings)
OPENAI_API_KEY=sk-...

# Pinecone (Vector Database)
PINECONE_API_KEY=...

# PostgreSQL (Metadata Storage)
POSTGRES_HOST=localhost
POSTGRES_DB=nong_unjai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=...
POSTGRES_PORT=5432

# Redis (Caching)
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 🚀 Quick Start

### 1. Initialize Knowledge Base

```python
from module_1_the_brain import KnowledgeBase, VideoMetadata, CircleLevel

# สร้าง instance
kb = KnowledgeBase()

# เช็คสถานะ
print(kb.get_stats())
```

### 2. Add Video to Knowledge Base

```python
from module_1_the_brain import VideoMetadata, CircleLevel

video = VideoMetadata(
    video_id="yt_abc123",
    youtube_url="https://youtube.com/watch?v=abc123",
    title="การรักตัวเองตามพระคัมภีร์",
    description="คำสอนเกี่ยวกับการเห็นคุณค่าในตัวเอง",
    transcript="พระเจ้าทรงสร้างมนุษย์ตามพระฉายของพระองค์...",
    summary="คำสอนเรื่อง self-worth และการรักตัวเอง",
    duration_seconds=600,
    circle_level=CircleLevel.SELF,  # 1 = Self, 2 = Close Ones, 3 = Society
    topic_tags=["self-love", "identity", "healing"],
    scripture_refs=[
        {"book": "Genesis", "chapter": 1, "verse": "27", "thai_book": "ปฐมกาล"}
    ],
    tone="gentle",  # gentle, energetic, urgent, comforting
    pastor_name="Pastor Somchai",
    language="th"
)

# Add to knowledge base
success = kb.add_video(video)
print(f"Added: {success}")
```

### 3. Search Videos

```python
# Search ด้วยข้อความ (semantic search)
results = kb.search(
    query="รู้สึกไม่มีค่า อยากได้กำลังใจ",
    user_circle_level=CircleLevel.SELF,
    top_k=5
)

for result in results:
    print(f"📹 {result.metadata.title}")
    print(f"   Score: {result.score:.3f}")
    print(f"   Circle: {result.metadata.circle_level.name}")
    print(f"   Tags: {', '.join(result.metadata.topic_tags)}")
```

### 4. Get Personalized Recommendations

```python
# แนะนำตาม mood และ circle level
recommendations = kb.get_recommendations(
    user_circle_level=CircleLevel.SELF,
    watched_videos=["yt_abc123"],  # วิดีโอที่ดูแล้ว
    mood="sad"  # sad, anxious, angry, or None
)

for rec in recommendations:
    print(f"💡 Recommended: {rec.metadata.title}")
```

## 📁 File Structure

```
module_1_the_brain/
├── module_1_the_brain.py    # Main module
├── requirements.txt         # Dependencies
├── README.md               # This file
└── tests/                  # Unit tests
    ├── test_embedding.py
    ├── test_vector_db.py
    └── test_metadata.py
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_vector_db.py -v
```

## 🔍 Key Components

### 1. EmbeddingGenerator
สร้าง vector embeddings จากข้อความโดยใช้ OpenAI API

```python
from module_1_the_brain import EmbeddingGenerator

gen = EmbeddingGenerator()
embedding = gen.generate("ข้อความที่ต้องการแปลงเป็น vector")
print(len(embedding))  # 1536 dimensions
```

### 2. VectorDatabase
จัดการ Pinecone index สำหรับ semantic search

```python
from module_1_the_brain import VectorDatabase

vdb = VectorDatabase()

# Search
results = vdb.search(
    query_embedding=embedding,
    circle_level=CircleLevel.SELF,
    top_k=5
)
```

### 3. MetadataStore
เก็บ metadata แบบเต็มใน PostgreSQL

```python
from module_1_the_brain import MetadataStore

store = MetadataStore()
store.save_video(video_metadata, pinecone_id="yt_123")

# Retrieve
video = store.get_video("yt_123")
```

### 4. KnowledgeBase
Interface หลักที่รวมทุก component

```python
from module_1_the_brain import KnowledgeBase

kb = KnowledgeBase()
kb.add_video(video)
results = kb.search("query")
```

## 📊 3 Circles Logic

ระบบจัดหมวดหมู่เนื้อหาตาม 3 ระดับ:

| Circle | ระดับ | หัวข้อ | ตัวอย่าง |
|--------|-------|--------|----------|
| 1 | SELF | การรักตัวเอง | self-esteem, healing, identity, burnout |
| 2 | CLOSE_ONES | ความสัมพันธ์ | family, marriage, friendship, communication |
| 3 | SOCIETY | สังคม | volunteering, leadership, social impact |

```python
from module_1_the_brain import CircleLevel

# Filter search by circle
results = kb.search(
    query="ความสัมพันธ์ในครอบครัว",
    user_circle_level=CircleLevel.CLOSE_ONES
)
```

## 🛠️ Utility Functions

### Chunk Transcript
แบ่ง transcript เป็นส่วนเล็กๆ สำหรับ embedding

```python
from module_1_the_brain import chunk_transcript

chunks = chunk_transcript(
    transcript="ข้อความยาวๆ...",
    chunk_size=400,  # จำนวนตัวอักษร
    overlap=50       # ทับซ้อนกัน
)
```

### Extract Scripture References
ดึงข้อพระคัมภีร์จากข้อความ

```python
from module_1_the_brain import extract_scripture_references

text = "ยอห์น 3:16 บอกว่าพระเจ้าทรงรักโลก"
refs = extract_scripture_references(text)
# [{'book': 'John', 'chapter': 3, 'verse': '16', 'thai_book': 'ยอห์น', ...}]
```

## 🔐 Error Handling & Retry

Module นี้มี built-in retry mechanism สำหรับ API calls:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def api_call():
    # Will retry 3 times with exponential backoff
    pass
```

## 📈 Performance Tips

1. **Caching**: Redis cache ผลลัพธ์ search ไว้ 5 นาที
2. **Batch Processing**: ใช้ `generate_batch()` สำหรับหลายข้อความ
3. **Index Tuning**: Pinecone ใช้ cosine similarity สำหรับ semantic search
4. **Database Index**: PostgreSQL มี index บน circle_level และ topic_tags

## 🐛 Troubleshooting

### Pinecone Connection Error
```
Error initializing index: Unauthorized
```
**Fix**: ตรวจสอบ `PINECONE_API_KEY` ใน environment variables

### PostgreSQL Connection Error
```
Error saving video: connection refused
```
**Fix**: ตรวจสอบว่า PostgreSQL running และ credentials ถูกต้อง

### OpenAI Rate Limit
```
RateLimitError: You exceeded your current quota
```
**Fix**: ใช้ `generate_batch()` และเพิ่ม delay ระหว่าง requests

## 📚 API Reference

ดู docstrings ใน `module_1_the_brain.py` สำหรับรายละเอียดเพิ่มเติม

## 🔗 Integration with Other Modules

Module 1 จะถูกเรียกใช้โดย:
- **Module 2**: NLP Processor (สำหรับ search หลังวิเคราะห์ intent)
- **Module 3**: Video Processing (บันทึก metadata หลังตัดต่อ)
- **Module 4**: LINE Gateway (ค้นหาคลิปตอบ user)

## 👥 Agents ที่เกี่ยวข้อง

| Agent | บทบาทใน Module นี้ |
|-------|-------------------|
| Archivist | จัดการ embeddings, chunking, metadata |
| Search Specialist | Semantic search, intent matching |
| Journey Architect | ใช้ข้อมูล circle level สำหรับ recommendations |

## 📝 License

สำหรับโครงการ Nong Unjai AI เท่านั้น
