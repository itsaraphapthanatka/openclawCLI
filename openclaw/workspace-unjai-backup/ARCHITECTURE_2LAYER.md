# Nong Unjai AI - 2 Layer Architecture

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      NONG UNJAI AI SYSTEM                        │
│                     (2-Layer Architecture)                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────┐     ┌─────────────────────────────┐
│      LAYER 1: PROD          │     │     LAYER 2: DEV/TEST       │
│    (LINE OA - Production)   │     │  (Telegram + Dev Interface) │
└─────────────────────────────┘     └─────────────────────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────────────────────┐     ┌─────────────────────────────┐
│  👤 End Users (Public)      │     │  👨‍💻 Dev Team (Internal)    │
│                             │     │                             │
│  • ผู้ใช้ทั่วไป            │     │  • Developers               │
│  • ผู้เชื่อ/ผู้สนใจ         │     │  • QA Testers               │
│  • อาสาสมัคร              │     │  • Admin                    │
│                             │     │                             │
│  Platform: LINE OA          │     │  Platform: Telegram         │
└─────────────────────────────┘     └─────────────────────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────────────────────┐     ┌─────────────────────────────┐
│     SAME CORE SYSTEM        │◄────┤      SAME CORE SYSTEM       │
├─────────────────────────────┤     ├─────────────────────────────┤
│                             │     │                             │
│  📚 Knowledge Source:       │     │  📚 Knowledge Source:       │
│  MEMORY.md ONLY             │     │  MEMORY.md ONLY             │
│                             │     │                             │
│  (ข้อมูลจากไฟล์ Word        │     │  (ข้อมูลจากไฟล์ Word        │
│   ที่ผ่านการ Chunking)      │     │   ที่ผ่านการ Chunking)      │
│                             │     │                             │
│  ❌ ไม่ใช้ข้อมูลนอก         │     │  ❌ ไม่ใช้ข้อมูลนอก         │
│     (No external AI)        │     │     (No external AI)        │
│                             │     │                             │
└─────────────────────────────┘     └─────────────────────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────────────────────┐     ┌─────────────────────────────┐
│   STRICT RULES (Both)       │     │   STRICT RULES (Both)       │
├─────────────────────────────┤     ├─────────────────────────────┤
│  ✓ ตอบจาก MEMORY.md เท่านั้น│     │  ✓ ตอบจาก MEMORY.md เท่านั้น│
│  ✓ ถามชื่อเล่นก่อนเสมอ      │     │  ✓ ถามชื่อเล่นก่อนเสมอ      │
│  ✓ ใช้คำลงท้าย คะ/ขา/นะคะ   │     │  ✓ ใช้คำลงท้าย คะ/ขา/นะคะ   │
│  ✓ 12 Personas              │     │  ✓ 12 Personas              │
│  ✓ Crisis Detection         │     │  ✓ Crisis Detection         │
│  ✓ R-Score Tracking         │     │  ✓ R-Score Tracking         │
│  ✓ Smart Coins              │     │  ✓ Smart Coins              │
└─────────────────────────────┘     └─────────────────────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────────────────────┐     ┌─────────────────────────────┐
│   DIFFERENCES               │     │   DIFFERENCES               │
├─────────────────────────────┤     ├─────────────────────────────┤
│                             │     │                             │
│  • Production DB            │     │  • Test DB (แยก)            │
│  • Real LINE Channel        │     │  • Telegram Bot              │
│  • All features ON          │     │  • Debug Mode ON             │
│  • Analytics ON             │     │  • Verbose Logging           │
│  • Nudge Scheduler ON       │     │  • Test Commands Available   │
│  • Coin Rewards: Real       │     │  • Coin Rewards: Simulated   │
│                             │     │  • Reset Data Allowed        │
│                             │     │                             │
│  ENV: PROD                  │     │  ENV: DEV/TEST               │
└─────────────────────────────┘     └─────────────────────────────┘
```

---

## 🔷 Layer 1: LINE OA (Production)

### หน้าที่
- ให้บริการผู้ใช้ทั่วไป
- ตอบคำถามจาก MEMORY.md เท่านั้น
- สะสม Smart Coins (จริง)
- Crisis Detection แจ้งอาสาจริง

### ข้อมูลที่ใช้
```
📚 MEMORY.md ONLY
   ├── ข้อมูลจากไฟล์ Word (ผ่าน chunking)
   ├── Scripture verses
   ├── Video references
   └── Metadata (circle tags, topics)

❌ ไม่ใช้:
   ├── External AI knowledge
   ├── Internet search
   └── Training data นอก MEMORY.md
```

### Tech Stack
```
LINE OA ←→ Webhook → FastAPI Gateway → Orchestrator → Memory Search
```

---

## 🔶 Layer 2: Telegram Dev/Test

### หน้าที่
- ให้ Dev Team ทดสอบระบบ
- ตอบคำถามจาก MEMORY.md เท่านั้น
- ทดสอบ Persona switching
- ทดสอบ Crisis detection
- Reset/ล้างข้อมูลได้

### ข้อมูลที่ใช้
```
📚 MEMORY.md ONLY (เหมือน Layer 1 เป๊ะ!)
   ├── ข้อมูลจากไฟล์ Word (ผ่าน chunking)
   ├── Scripture verses
   ├── Video references
   └── Metadata (circle tags, topics)

❌ ไม่ใช้ (เหมือนกัน):
   ├── External AI knowledge
   ├── Internet search
   └── Training data นอก MEMORY.md
```

### Extra Features (Dev Only)
```
✓ /reset - ล้างประวัติการคุย
✓ /persona <1-12> - สลับ persona ทันที
✓ /debug - ดู debug info
✓ /test_crisis - ทดสอบ crisis detection
✓ /simulate <scenario> - จำลองสถานการณ์
✓ /memory_info - ดูข้อมูลที่ค้นหาได้
```

### Tech Stack
```
Telegram Bot ←→ Webhook → FastAPI Gateway → Orchestrator → Memory Search
```

---

## ⚖️ เปรียบเทียบ Layer 1 vs Layer 2

| Feature | Layer 1 (LINE) | Layer 2 (Telegram) |
|---------|----------------|-------------------|
| **Knowledge Source** | MEMORY.md only | MEMORY.md only |
| **ถามชื่อเล่น** | ✅ ทุกครั้ง | ✅ ทุกครั้ง |
| **คำลงท้าย** | คะ/ขา/นะคะ | คะ/ขา/นะคะ |
| **12 Personas** | ✅ | ✅ |
| **Crisis Detection** | ✅ แจ้งจริง | ✅ แจ้ง test channel |
| **Smart Coins** | ✅ จริง | ⚠️ Simulated |
| **R-Score** | ✅ Track จริง | ✅ Track แยก |
| **Database** | Production | Test (แยก) |
| **Debug Mode** | ❌ OFF | ✅ ON |
| **Test Commands** | ❌ ไม่มี | ✅ มี |
| **Reset Data** | ❌ ไม่ได้ | ✅ ได้ |

---

## 🎯 เป้าหมายของแต่ละ Layer

### Layer 1 (LINE) - PRODUCTION
```
🎯 Goal: ให้บริการผู้ใช้จริง
🎯 Users: ประชาชนทั่วไป
🎯 Data: Production Database
🎯 Stability: สูงสุด
🎯 Monitoring: ครบทุกอย่าง
```

### Layer 2 (Telegram) - DEV/TEST
```
🎯 Goal: ทดสอบระบบก่อน deploy
🎯 Users: Dev Team เท่านั้น
🎯 Data: Test Database (แยก)
🎯 Stability: รับได้ถ้ามีบั๊ก
🎯 Monitoring: Verbose logging
```

---

## 🔧 Implementation Plan

### Step 1: Shared Core
```python
# core/ - ใช้ร่วมกันทั้ง 2 Layer
├── memory_engine.py      # Search MEMORY.md
├── persona_manager.py    # 12 Personas
├── nlp_processor.py      # Intent + Sentiment
├── crisis_detector.py    # SOSVE Protocol
└── response_builder.py   # Build response
```

### Step 2: Layer 1 Adapter
```python
# layer1/ - LINE OA
├── line_gateway.py       # Webhook handler
├── line_flex_builder.py  # LINE Flex Messages
└── line_bot.py          # Main bot
```

### Step 3: Layer 2 Adapter
```python
# layer2/ - Telegram Dev
├── telegram_gateway.py   # Webhook handler
├── telegram_commands.py  # Dev commands
├── debug_tools.py       # Debug features
└── telegram_bot.py      # Main bot
```

---

## 📋 Checklist สำหรับ Dev Team

### Before Testing (Layer 2)
- [ ] ใช้ Telegram Bot (ไม่ใช่ LINE)
- [ ] Database เป็น Test DB
- [ ] Debug mode ON
- [ ] มีสิทธิ์ reset data

### Before Deploy (Layer 1)
- [ ] ทดสอบผ่าน Layer 2 เรียบร้อย
- [ ] QA Report ผ่าน 95%
- [ ] ใช้ Production DB
- [ ] LINE Channel ถูกต้อง
- [ ] Monitoring ทำงาน

---

## ✅ Key Principles

1. **Same Core**: ทั้ง 2 Layer ใช้ Core Logic เดียวกัน
2. **Same Memory**: ทั้ง 2 Layer อ่านจาก MEMORY.md เดียวกัน
3. **Same Rules**: ทั้ง 2 Layer ใช้กฎเดียวกัน (คะ/ขา/ถามชื่อ/12 Personas)
4. **Separate Data**: Database แยกกัน (Production vs Test)
5. **Extra Dev Tools**: Layer 2 มีเครื่องมือทดสอบเพิ่ม

---

## 🚫 สิ่งที่ห้ามทำ

### ห้ามใน Layer 1 (LINE)
- ห้ามใช้ข้อมูลนอก MEMORY.md
- ห้ามทดสอบโดยไม่ผ่าน Layer 2
- ห้าม reset ข้อมูลผู้ใช้

### ห้ามใน Layer 2 (Telegram)
- ห้ามใช้ข้อมูลนอก MEMORY.md (เหมือนกัน!)
- ห้ามเชื่อมต่อ Production DB
- ห้ามส่ง Crisis Alert จริง

---

## 📞 Contact

- **Layer 1 Issues**: #production-support
- **Layer 2 Issues**: #dev-testing
- **Core Logic**: #architecture-team
