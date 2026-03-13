# Module 3: Main Orchestrator (The Brain of the Swarm)

## 📚 Overview

Module นี้เป็น **"สมองกลาง"** ของระบบ Nong Unjai AI รับผิดชอบ:
- **Central Controller** - รับ request จาก LINE Gateway แล้วจัดการ workflow
- **Intent Routing** - ส่งต่อไปยัง handler ที่เหมาะสมตาม intent
- **Module Coordination** - เรียกใช้ NLP, Knowledge Base, Middleware ตามลำดับ
- **Crisis Management** - ตรวจจับและจัดการสถานการณ์วิกฤต
- **Session Updates** - อัปเดต persona, circle, R-score ให้ UserSession

## 🏗️ Architecture

```
User Message
    ↓
LINE Gateway (Module 4)
    ↓
Main Orchestrator (Module 3)
    ├── Step 1: NLP Analysis (Module 2)
    ├── Step 2: Crisis Check
    ├── Step 3: Intent Routing
    │   ├── Greeting → _handle_greeting
    │   ├── Bible Question → _handle_bible_question
    │   ├── Emotional Support → _handle_emotional_support
    │   ├── Video Request → Middleware
    │   └── ...etc
    ├── Step 4: Knowledge Search (Module 1)
    └── Step 5: Build Response
    ↓
Response to User
```

## 📦 Installation

```bash
# Dependencies (already in requirements.txt)
pip install httpx

# Import in your code
from module_3_main_orchestrator import MainOrchestrator, OrchestratedLineGateway
```

## 🚀 Quick Start

### 1. Basic Usage

```python
import asyncio
from module_3_main_orchestrator import MainOrchestrator
from module_4_line_gateway import UserSession

async def main():
    # Initialize orchestrator
    orchestrator = MainOrchestrator()
    
    # Mock user session
    session = UserSession(user_id="Uxxx123")
    
    # Process message
    result = await orchestrator.process_message(
        user_id="Uxxx123",
        message="วันนี้รู้สึกนอยๆ",
        session=session
    )
    
    print(result)
    # {
    #     "type": "text",
    #     "content": "อุ่นใจเข้าใจความรู้สึก...",
    #     "persona": 2,
    #     "intent": "emotional_support"
    # }

asyncio.run(main())
```

### 2. Integration with LINE Gateway

```python
from module_3_main_orchestrator import OrchestratedLineGateway
from module_4_line_gateway import create_app
import uvicorn

# Create integrated gateway
integrated = OrchestratedLineGateway()

# Create FastAPI app
app = create_app(integrated.line_gateway)

# Run
uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 📊 Workflow Steps

| Step | หน้าที่ | Module ที่ใช้ |
|------|---------|---------------|
| 1. Analyze | วิเคราะห์ข้อความ | Module 2 (NLP) |
| 2. Check Crisis | ตรวจสอบวิกฤต | Module 2 (CrisisDetector) |
| 3. Route Intent | กำหนด handler | Main Orchestrator |
| 4. Search Knowledge | ค้นหาข้อมูล | Module 1 (Knowledge Base) |
| 5. Build Response | สร้างคำตอบ | Module 4 (Flex Builder) |

## 🎯 Intent Handlers

| Intent | Handler | Persona ที่แนะนำ |
|--------|---------|------------------|
| `greeting` | `_handle_greeting` | 6 (Watcher) |
| `small_talk` | `_handle_small_talk` | 3 (Social) |
| `emotional_support` | `_handle_emotional_support` | 2 (Healing) |
| `bible_question` | `_handle_bible_question` | 1 (Intellectual) |
| `theology_question` | `_handle_bible_question` | 1 (Intellectual) |
| `crisis` | `_handle_crisis` | 8 (SOS) |
| `request_video` | `_handle_video_request` | 2/3 (Healing/Social) |
| `quiz_answer` | `_handle_quiz_answer` | 11 (Gamer) |
| `gratitude` | `_handle_gratitude` | 6 (Watcher) |
| `complaint` | `_handle_emotional_support` | 2 (Healing) |
| `goodbye` | `_handle_goodbye` | 6 (Watcher) |
| `unknown` | `_handle_unknown` | 6 (Watcher) |

## 🚨 Crisis Handling

```python
# Crisis is detected in Step 2
if context.is_crisis:
    context.recommended_persona = 8  # Force SOS Persona
    return await self._build_crisis_response(context, session)

# Response includes emergency contacts
crisis_response = {
    "type": "text",
    "content": (
        "คุณพี่คะ! หยุดก่อนนะคะ!...\n\n"
        "☎️ สายด่วนสุขภาพจิต: 1323\n"
        "☎️ หน่วยกู้ชีพ: 1669"
    ),
    "crisis_alert": True,
    "persona": 8
}
```

## 🔄 Middleware Integration

```python
# Set callbacks for external services
orchestrator.set_video_callback(my_video_service)
orchestrator.set_quiz_callback(my_quiz_service)
orchestrator.set_coin_callback(my_coin_service)

# Callback signature
async def video_callback(query: str) -> Dict:
    # Call your middleware
    response = await httpx.post(
        "http://middleware/api/video",
        json={"query": query}
    )
    return response.json()
```

## 📝 WorkflowContext

ข้อมูลที่ถูกส่งผ่านทุก step:

```python
@dataclass
class WorkflowContext:
    user_id: str
    message: str
    sentiment_score: float        # -1.0 to 1.0
    sentiment_label: str          # POSITIVE/NEGATIVE/etc
    primary_intent: IntentType    # greeting/bible/etc
    intent_confidence: float
    emotions: List[str]           # [sad, tired]
    crisis_level: str             # NONE/WARNING/EMERGENCY
    is_crisis: bool
    r_score: float                # 0-100
    recommended_persona: int      # 1-12
    recommended_circle: int       # 1-3
    knowledge_results: List[Dict] # Search results
    video_url: Optional[str]      # From middleware
    response_type: str            # text/flex/quick_reply
    response_content: str
    response_data: Dict           # Flex content, options
    processing_time_ms: int
    steps_executed: List[str]     # Audit trail
```

## 🎭 Persona Switching

Orchestrator จะกำหนด Persona ตาม:

```python
# 1. Crisis override (สูงสุด)
if context.is_crisis:
    return 8  # SOS

# 2. Intent-based
intent_personas = {
    IntentType.BIBLE_QUESTION: 1,      # Intellectual
    IntentType.EMOTIONAL_SUPPORT: 2,   # Healing
    IntentType.GREETING: 6,            # Watcher
    IntentType.REQUEST_VIDEO: 3,       # Social
}

# 3. Sentiment-based fallback
if sentiment < -0.3: return 2  # Healing
if sentiment > 0.3: return 3   # Social
```

## 📊 Response Types

### Text Response
```python
{
    "type": "text",
    "content": "สวัสดีค่ะ!",
    "persona": 6
}
```

### Flex Message (Video Card)
```python
{
    "type": "flex",
    "content": "...",
    "flex_content": {...},
    "alt_text": "Video title",
    "persona": 2
}
```

### Quick Reply
```python
{
    "type": "quick_reply",
    "content": "เลือกได้เลยค่ะ!",
    "options": [
        {"label": "🎥 ขอคลิป", "text": "ขอคลิป"},
        {"label": "📖 พระคัมภีร์", "text": "พระคัมภีร์"},
    ],
    "persona": 6
}
```

## 🧪 Testing

```bash
# Run built-in tests
python module_3_main_orchestrator.py
```

Expected output:
```
======================================================================
🎛️ Main Orchestrator Test
======================================================================

📝 Test: Greeting
   Input: 'สวัสดีค่ะ'
   Type: text
   Persona: 6
   Intent: greeting
   Response: สวัสดีค่ะ! น้องอุ่นใจยินดีที่ได้รู้จัก...

📝 Test: Emotional support
   Input: 'วันนี้รู้สึกนอยๆ'
   Type: text
   Persona: 2
   Intent: emotional_support
   Response: อุ่นใจเข้าใจความรู้สึก...

📝 Test: Crisis
   Input: 'อยากตาย ไม่อยากอยู่แล้ว'
   Type: text
   Persona: 8
   Intent: crisis
   Response: คุณพี่คะ! หยุดก่อนนะคะ!...
```

## 🔗 Module Integration

```
┌─────────────────────────────────────────────────────────┐
│                    Main Orchestrator                     │
├─────────────────────────────────────────────────────────┤
│  Module 2 (NLP) ◄─────────────────► Sentiment/Intent   │
│       ↓                                                │
│  Crisis? ──Yes──► Persona 8 + Alert                    │
│       │ No                                             │
│       ↓                                                │
│  Route Intent                                          │
│       ↓                                                │
│  ├─► Module 1 (Knowledge) ──► Bible answers            │
│  ├─► Middleware ────────────► Video/Quiz               │
│  └─► Internal ──────────────► Greeting/Support         │
│       ↓                                                │
│  Module 4 (LINE Gateway) ◄──► Send response            │
└─────────────────────────────────────────────────────────┘
```

## ⚙️ Configuration

```python
from module_3_main_orchestrator import OrchestratorConfig

config = OrchestratorConfig(
    middleware_video_url="http://middleware:8000/api/video",
    middleware_quiz_url="http://middleware:8000/api/quiz",
    knowledge_base_url="http://localhost:8001",
    maac_api_url="http://maac:8000/api",
    r_score_low_threshold=40.0,
    r_score_high_threshold=80.0,
    video_request_timeout=30
)

orchestrator = MainOrchestrator(config)
```

## 📝 Environment Variables

```env
# Middleware endpoints
MIDDLEWARE_VIDEO_URL=http://localhost:8002/api/video
MIDDLEWARE_QUIZ_URL=http://localhost:8002/api/quiz

# Knowledge base
KNOWLEDGE_BASE_URL=http://localhost:8001

# MAAC (optional)
MAAC_API_URL=http://localhost:8003/api
```

## 👥 Agents ที่เกี่ยวข้อง

| Agent | บทบาทใน Module นี้ |
|-------|-------------------|
| **Main Orchestrator** | Central controller |
| **Journey Architect** | R-score calculation, Circle transition |
| **Front-Desk Agent** | Route to appropriate Persona |
| **Sentinel Agent** | Crisis detection trigger |

## 🔮 Future Improvements

- [ ] Multi-turn conversation context
- [ ] Fallback to human agent
- [ ] A/B testing for responses
- [ ] Real-time analytics streaming
- [ ] Dynamic intent learning

## 📚 Dependencies

```
httpx>=0.24.0
module_2_nlp_processor  (local)
module_4_line_gateway   (local)
```
