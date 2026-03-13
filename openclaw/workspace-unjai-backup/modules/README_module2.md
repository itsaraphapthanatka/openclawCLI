# Module 2: NLP Processor (The Mind Reader)

## 📚 Overview

Module นี้เป็น **"สมองด้านภาษา"** ของระบบ Nong Unjai AI รับผิดชอบ:
- **Sentiment Analysis** - วิเคราะห์อารมณ์ (Thai + English) พร้อมคะแนน -1.0 ถึง 1.0
- **Intent Classification** - จำแนกประเภทคำถาม (greeting, bible, crisis, etc.)
- **R-score Calculation** - คำนวณคะแนนสภาวะจิตใจ
- **Crisis Detection (SOSVE)** - ตรวจจับวิกฤตฆ่าตัวตายและ alert
- **Entity Extraction** - ดึง emotions, topics จากข้อความ
- **Persona Recommendation** - แนะนำ Persona 1-12 ตาม context

## 🏗️ Architecture

```
Module 2: NLP Processor
├── ThaiTextProcessor      # ทำความสะอาด + tokenize ภาษาไทย
├── SentimentAnalyzer      # วิเคราะห์อารมณ์ (Transformers)
├── IntentClassifier       # จำแนก intent (Regex + Heuristics)
├── CrisisDetector         # ตรวจจับ crisis keywords (SOSVE)
├── PersonaRecommender     # แนะนำ persona ตามผลวิเคราะห์
└── NLPProcessor (Main)    # Interface หลัก
```

## 📦 Installation

```bash
# Dependencies (add to requirements.txt)
pip install transformers torch numpy

# Optional: Thai NLP
pip install pythainlp
```

## 🚀 Quick Start

### 1. Initialize NLP Processor

```python
from module_2_nlp_processor import NLPProcessor

# Initialize
processor = NLPProcessor(
    sentiment_model="airesearch/wangchanberta-base-att-spm-uncased",
    enable_gpu=False
)

# Check health
print(processor.get_health())
```

### 2. Analyze Single Message

```python
# Analyze user message
result = processor.analyze("วันนี้รู้สึกนอยๆ ตั้งแต่เช้า")

print(f"Sentiment: {result.sentiment.label.name}")  # NEGATIVE
print(f"Intent: {result.intent.primary_intent.value}")  # emotional_support
print(f"R-Score: {result.r_score:.1f}")  # 0-100
print(f"Crisis Level: {result.crisis.level.name}")  # NONE / WARNING / EMERGENCY
print(f"Recommended Persona: {result.recommended_persona}")  # 1-12
```

### 3. Crisis Detection Example

```python
# Crisis message
result = processor.analyze("อยากตาย ไม่อยากอยู่แล้ว")

if result.crisis.is_crisis:
    print("🚨 SOSVE TRIGGERED!")
    print(f"Level: {result.crisis.level.name}")  # EMERGENCY
    print(f"Keywords: {result.crisis.trigger_keywords}")
    print(f"Alert Human: {result.crisis.should_alert_human}")  # True
    print(f"Use Persona: {result.recommended_persona}")  # 8 (SOS)
```

## 📊 Output Format

```python
{
    "original_text": "วันนี้รู้สึกนอยๆ",
    "cleaned_text": "วันนี้รู้สึกเศร้า",
    "sentiment": {
        "score": -0.65,
        "label": "NEGATIVE",
        "confidence": 0.85,
        "emotions": ["sad", "tired"],
        "explanation": "Detected emotions: sad, tired. Overall sentiment: NEGATIVE"
    },
    "intent": {
        "primary": "emotional_support",
        "confidence": 0.8,
        "secondary": [("complaint", 0.3)],
        "entities": {
            "emotions": ["sad"],
            "topics": [],
            "has_question_mark": False,
            "message_length": 15,
            "word_count": 4
        }
    },
    "r_score": 42.5,  # 0-100
    "crisis": {
        "is_crisis": False,
        "level": "NONE",
        "trigger_keywords": [],
        "should_alert": False
    },
    "recommended_persona": 2,  # เพื่อนสาวสายเยียวยา
    "recommended_circle": 1,   # SELF
    "processing_time_ms": 120
}
```

## 🎯 Intent Types

| Intent | คำอธิบาย | ตัวอย่าง |
|--------|----------|----------|
| `greeting` | ทักทาย | "สวัสดี", "หวัดดี" |
| `small_talk` | คุยเล่น | "เป็นไงบ้าง", "ทำอะไรอยู่" |
| `emotional_support` | ต้องการเยียวยา | "นอยๆ", "เหนื่อยจัง" |
| `bible_question` | ถามพระคัมภีร์ | "ยอห์น 3:16 ว่าอะไร" |
| `theology_question` | ถามปรัชญา | "พระเจ้ามีจริงปะ" |
| `crisis` | วิกฤต | "อยากตาย", "ไม่ไหวแล้ว" |
| `request_video` | ขอคลิป | "ขอคลิปหนุนใจ" |
| `quiz_answer` | ตอบควิซ | "ตอบ A", "ข้อ 2" |
| `gratitude` | ขอบคุณ | "ขอบคุณนะ" |
| `complaint` | บ่น/ระบาย | "แย่จัง", "โมโห" |
| `goodbye` | ลาก่อน | "บาย", "ลาก่อน" |

## 🚨 SOSVE Crisis Detection

### Crisis Levels

| Level | Trigger | Action |
|-------|---------|--------|
| **NONE** | ไม่มี keyword อันตราย | ดำเนินการปกติ |
| **WARNING** | Sentiment < -0.7 หรือ warning keywords | ใช้ Persona 2 (เยียวยา), monitor |
| **EMERGENCY** | Critical keywords หรือ sentiment < -0.9 | **Persona 8 (SOS) + Alert human** |

### Critical Keywords (Trigger Persona 8)

```python
CRITICAL_KEYWORDS = [
    "อยากตาย", "ไม่อยากอยู่แล้ว", "ลาก่อน", "จบปัญหา",
    "ฆ่าตัวตาย", "ทำร้ายตัวเอง", "หลับไม่ตื่น",
    "ไม่ไหวแล้ว", "มืดแปดด้าน", "ไม่มีทางออก",
    "ไม่เหลืออะไรแล้ว", "ไร้ค่า", "ไม่มีความหมาย"
]
```

## 🎭 Persona Recommendation Logic

```python
# Crisis override
if crisis.level == EMERGENCY:
    return Persona 8  # SOS

# Intent-based
if intent == CRISIS: return Persona 8
if intent == BIBLE_QUESTION: return Persona 1
if intent == EMOTIONAL_SUPPORT: return Persona 2
if intent == GREETING: return Persona 6

# Sentiment-based fallback
if sentiment < -0.3: return Persona 2  # Healing
if sentiment > 0.3: return Persona 3   # Energetic
```

## 📈 R-Score Calculation

```
R-score = (S × 0.4) + (Q × 0.3) + (I × 0.3)

Where:
- S (Sentiment): 0-100 (จาก sentiment score)
- Q (Quiz): 0-100 (จากผลทำควิซ)
- I (Interaction): 0-100 (จากความถี่ใช้งาน)
```

**R-score Ranges:**
- 0-40: ต้องการการดูแลมาก (Circle 1 focus)
- 41-60: ปานกลาง (Circle 1-2)
- 61-80: ดี (Circle 2-3)
- 81-100: พร้อมช่วยเหลือคนอื่น (Circle 3)

## 🔧 Thai Text Processing

### Cleaning

```python
from module_2_nlp_processor import ThaiTextProcessor

processor = ThaiTextProcessor()
cleaned = processor.clean_text("นอยยย มากกก ค่ะ")
# Output: "นอย มาก คะ"
```

### Emotion Extraction

```python
emotions = processor.extract_emotion_words("วันนี้เศร้า โกรธแฟนมาก")
# Output: ["sad", "angry"]
```

## 🧪 Testing

```python
# Run built-in tests
python module_2_nlp_processor.py
```

Expected output:
```
======================================================================
🧠 NLP Processor Test Results
======================================================================

📝 Input: สวัสดีค่ะ น้องอุ่นใจ
   Sentiment: SLIGHTLY_POSITIVE (0.45)
   Intent: greeting
   Crisis: NONE
   R-Score: 72.5
   Persona: 6
   Time: 85ms

📝 Input: อยากตาย ไม่อยากอยู่แล้ว
   Sentiment: VERY_NEGATIVE (-0.95)
   Intent: crisis
   Crisis: EMERGENCY
   R-Score: 15.0
   Persona: 8
   Time: 92ms
```

## 🔗 Integration with Module 1

```python
from module_1_the_brain import KnowledgeBase, CircleLevel
from module_2_nlp_processor import NLPProcessor

# Initialize both modules
nlp = NLPProcessor()
kb = KnowledgeBase()

# Process user message
analysis = nlp.analyze("รู้สึกไม่มีค่า อยากได้กำลังใจ")

# Use results to search videos
results = kb.search(
    query=analysis.cleaned_text,
    user_circle_level=CircleLevel(analysis.recommended_circle),
    top_k=5
)

# Select persona for response
persona_id = analysis.recommended_persona
if analysis.crisis.should_alert_human:
    trigger_sos_alert(analysis)
```

## 📊 Performance

| Task | Average Time | Notes |
|------|--------------|-------|
| Sentiment Analysis | 50-100ms | With transformer model |
| Intent Classification | 5-10ms | Regex-based |
| Crisis Detection | 1-2ms | Keyword matching |
| Full Analysis | 80-150ms | End-to-end |

## 🛠️ Configuration

### Environment Variables

```env
# Optional: Custom model
SENTIMENT_MODEL=airesearch/wangchanberta-base-att-spm-uncased

# Optional: GPU
USE_GPU=true
```

### Custom Crisis Keywords

```python
from module_2_nlp_processor import CrisisDetector

detector = CrisisDetector()
detector.CRITICAL_KEYWORDS.append("คำใหม่ที่ต้องการเพิ่ม")
```

## 📝 API Reference

### NLPProcessor

```python
class NLPProcessor:
    def __init__(self, sentiment_model=None, enable_gpu=False)
    def analyze(self, text: str, user_history=None) -> NLPAnalysisResult
    def batch_analyze(self, texts: List[str]) -> List[NLPAnalysisResult]
    def get_health(self) -> Dict
```

### CrisisDetector

```python
class CrisisDetector:
    def detect(self, text: str, sentiment_score: float) -> CrisisDetectionResult
```

### SentimentAnalyzer

```python
class SentimentAnalyzer:
    def analyze(self, text: str) -> SentimentResult
```

## 👥 Agents ที่เกี่ยวข้อง

| Agent | บทบาทใน Module นี้ |
|-------|-------------------|
| **Sentinel Agent** | Crisis detection + SOSVE triggering |
| **Journey Architect** | R-score calculation + Persona selection |
| **NLP Processor** | Main interface for text analysis |

## 🔮 Future Improvements

- [ ] Fine-tune Thai sentiment model on religious domain
- [ ] Add more sophisticated entity recognition
- [ ] Implement context-aware analysis (multi-turn)
- [ ] Add sarcasm detection
- [ ] Integrate with speech-to-text for voice messages

## 📚 Dependencies

```
transforms>=4.30.0
torch>=2.0.0
numpy>=1.24.0
pythainlp>=4.0.0  (optional)
```
