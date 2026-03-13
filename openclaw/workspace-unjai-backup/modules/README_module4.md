# Module 4: LINE Gateway (The Digital Receptionist)

## 📚 Overview

Module นี้เป็น **"ประตูสู่โลก LINE OA"** ของระบบ Nong Unjai AI รับผิดชอบ:
- **Webhook Handling** - รับ events จาก LINE (message, follow, postback)
- **Message Parsing** - แปลงข้อความ LINE เป็น format มาตรฐาน
- **Flex Message Builder** - สร้าง UI สวยงามบน LINE (cards, carousels, buttons)
- **Session Management** - จัดการสถานะผู้ใช้ด้วย Redis
- **Reply & Push Messages** - ส่งข้อความตอบกลับและ proactive messages

## 🏗️ Architecture

```
LINE Messaging API
       ↓
   Webhook (HTTPS)
       ↓
┌──────────────────┐
│  LINE Gateway    │
├──────────────────┤
│ • Signature      │
│   Verification   │
│ • Event Parsing  │
│ • Session Mgmt   │
│ • Flex Builder   │
└──────────────────┘
       ↓
   NLP Processor
       ↓
   Knowledge Base
```

## 📦 Installation

```bash
# Dependencies
pip install fastapi line-bot-sdk redis httpx uvicorn

# Set environment variables
export LINE_CHANNEL_ACCESS_TOKEN="your-token"
export LINE_CHANNEL_SECRET="your-secret"
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
```

## 🚀 Quick Start

### 1. Run Webhook Server

```python
from module_4_line_gateway import LineGateway, create_app
import uvicorn

# Initialize
gateway = LineGateway()

# Set handlers
async def handle_message(parsed, session):
    # Integrate with NLP Processor
    return {"type": "text", "content": "Hello!"}

gateway.set_message_handler(handle_message)

# Create and run app
app = create_app(gateway)
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Setup LINE Webhook URL

ใน LINE Developers Console:
1. Go to Messaging API → Webhook settings
2. Set URL: `https://your-domain.com/webhook`
3. Enable webhook
4. Verify (LINE จะส่ง request มาทดสอบ)

### 3. Test Webhook

```bash
curl -X POST https://your-domain.com/webhook \
  -H "Content-Type: application/json" \
  -H "X-Line-Signature: xxx" \
  -d '{
    "events": [{
      "type": "message",
      "message": {"type": "text", "text": "Hello", "id": "123"},
      "source": {"userId": "Uxxx", "type": "user"},
      "timestamp": 1234567890,
      "replyToken": "xxx"
    }]
  }'
```

## 📊 Message Types

| Type | Handler | ตัวอย่าง |
|------|---------|----------|
| `text` | ✅ | "สวัสดี" |
| `image` | ✅ | รูปภาพ |
| `sticker` | ✅ | Sticker |
| `video` | ⚠️ | วิดีโอ (ต้องดาวน์โหลด) |
| `postback` | ✅ | กดปุ่ม |
| `follow` | ✅ | เพิ่มเพื่อน |

## 💬 Flex Message Examples

### Video Card

```python
from module_4_line_gateway import FlexMessageBuilder

builder = FlexMessageBuilder()

video_card = builder.create_video_card(
    title="การรักตัวเองตามพระคัมภีร์",
    description="คำสอนเกี่ยวกับการเห็นคุณค่าในตัวเอง",
    video_url="https://your-cdn.com/video.mp4",
    thumbnail_url="https://your-cdn.com/thumb.jpg",
    duration="10:23",
    scripture="ปฐมกาล 1:27",
    tags=["self-love", "healing", "identity"]
)

# Send as Flex Message
response = {
    "type": "flex",
    "alt_text": "Video: การรักตัวเอง",
    "flex_content": video_card
}
```

### Quiz Card

```python
quiz_card = builder.create_quiz_card(
    question="พระเยซูทรงให้คำสอนเรื่องอะไรในบนภูเขา?",
    choices=[
        "คำอธิษฐาน",
        "คำเทศน์บนภูเขา",
        "อัศจรรย์",
        "การฟื้นคืนชีพ"
    ],
    quiz_id="quiz_001"
)
```

### User Progress Card

```python
progress_card = builder.create_progress_card(
    coins=150,
    r_score=72.5,
    circle_level=2,
    streak_days=5
)
```

### Carousel (Multiple Cards)

```python
bubbles = [
    video_card_1,
    video_card_2,
    video_card_3
]
carousel = builder.create_carousel(bubbles)
```

## 🔐 Signature Verification

LINE ส่ง signature ใน header `X-Line-Signature` เพื่อยืนยันว่า request มาจาก LINE จริง

```python
from module_4_line_gateway import LineGateway

gateway = LineGateway()

# Verify automatically in handle_webhook()
# Returns 401 if signature invalid
```

## 👤 Session Management

### User Session Structure

```python
{
    "user_id": "Uxxx...",
    "current_persona": 6,        # Active persona (1-12)
    "current_circle": 1,          # Circle level (1-3)
    "r_score": 72.5,              # Ready Heart Score
    "conversation_history": [],   # Last 10 messages
    "last_interaction": "2024-01-15T10:30:00",
    "message_count": 42,
    "crisis_flag": False
}
```

### Access Session

```python
session = gateway.session_manager.get_session(user_id)

# Update fields
gateway.session_manager.update_session(
    user_id,
    current_persona=2,
    r_score=65.0
)

# Add message to history
session.add_message("user", "Hello")
session.add_message("assistant", "Hi!")
gateway.session_manager.save_session(session)
```

## 🚨 Crisis Handling

```python
async def crisis_handler(parsed, session):
    # Check with NLP Processor
    analysis = nlp_processor.analyze(parsed.content)
    
    if analysis.crisis.level == "EMERGENCY":
        return {
            "is_crisis": True,
            "level": "EMERGENCY",
            "should_alert_human": True
        }
    
    return {"is_crisis": False}

gateway.set_crisis_handler(crisis_handler)
```

เมื่อเป็น crisis ระบบจะ:
1. ส่งข้อความ Persona 8 (SOS) ทันที
2. Log critical alert
3. รอ human intervention

## 📱 Quick Reply

```python
quick_reply = builder.create_quick_reply_buttons([
    {"label": "🎥 ขอคลิป", "text": "ขอคลิปหนุนใจ"},
    {"label": "📖 พระคัมภีร์", "text": "ข้อพระคัมภีร์วันนี้"},
    {"label": "🎯 ทำควิซ", "text": "อยากทำควิซ"},
])

response = {
    "type": "quick_reply",
    "content": "เลือกได้เลยค่ะ!",
    "options": quick_reply
}
```

## 🔄 Push Messages (Proactive)

ส่งข้อความถึง user โดยไม่ต้องรอ user ทักมาก่อน (ใช้สำหรับ nudges)

```python
# Send after 7 days inactive
await gateway.push_message(
    user_id="Uxxx...",
    message_data={
        "type": "text",
        "content": "แวะมาส่งกำลังใจให้ในเช้าวันใหม่นะคะ 🌅"
    }
)
```

## 🧪 Testing

```bash
# Run server
python module_4_line_gateway.py

# Test webhook (in another terminal)
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "events": [{
      "type": "message",
      "message": {"type": "text", "text": "Hello", "id": "123"},
      "source": {"userId": "Utest123", "type": "user"},
      "timestamp": 1234567890,
      "replyToken": "test-token"
    }]
  }'
```

## 📁 Project Structure

```
modules/
├── module_4_line_gateway.py   # Main module
├── example_usage_module4.py   # Examples
└── README_module4.md          # This file
```

## 🔗 Integration Flow

```
User sends message
    ↓
LINE Webhook → LINE Gateway
    ↓
Parse Event → Get Session
    ↓
Crisis Check → [ถ้า crisis → Persona 8]
    ↓
NLP Processor (Module 2)
    ↓
Knowledge Base (Module 1) [ถ้าต้องการ video]
    ↓
Select Persona (1-12)
    ↓
Build Flex Message
    ↓
Send Reply
```

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook` | POST | LINE webhook handler |
| `/health` | GET | Health check |
| `/stats` | GET | Gateway statistics |

## 📊 Environment Variables

```env
# Required
LINE_CHANNEL_ACCESS_TOKEN=xxx
LINE_CHANNEL_SECRET=xxx

# Optional (default: localhost)
REDIS_HOST=localhost
REDIS_PORT=6379

# Server
PORT=8000
HOST=0.0.0.0
```

## 👥 Agents ที่เกี่ยวข้อง

| Agent | บทบาทใน Module นี้ |
|-------|-------------------|
| **LINE Gateway** | Main interface (Agent #16) |
| **Session Manager** | Redis-based session storage |
| **Flex Builder** | UI component builder |

## 🔮 Future Improvements

- [ ] WebSocket support for real-time updates
- [ ] Rich Menu management
- [ ] Liff app integration
- [ ] Payment integration (LINE Pay)
- [ ] Multi-bot support
- [ ] Analytics dashboard

## 📚 Dependencies

```
fastapi>=0.100.0
line-bot-sdk>=3.0.0
redis>=5.0.0
httpx>=0.24.0
uvicorn>=0.23.0
pydantic>=2.0.0
```
