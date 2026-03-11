# Module 8: Nudge Scheduler (The Engagement Keeper)

## 📚 Overview

Module นี้เป็น **"ระบบทักทายอัตโนมัติ"** ของ Nong Unjai AI รับผิดชอบ:
- **Daily Verse** - ส่งข้อพระคัมภีร์ประจำวันให้ user ที่ opt-in
- **Inactive User Nudges** - ทักทาย user ที่ไม่ active (7, 14, 30 วัน)
- **Streak Reminders** - เตือนเมื่อ user มี streak สูงๆ
- **Cron Scheduling** - จัดการ schedule อัตโนมัติ

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Nudge Scheduler                  │
│  (APScheduler + Cron Jobs)              │
├─────────────────────────────────────────┤
│  08:00 → Daily Verse                    │
│  09:00 → Check Inactive Users           │
│  10:00 → Streak Reminders               │
└─────────────────────────────────────────┘
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
User (Push)       LINE Gateway
```

## 📦 Installation

```bash
# Dependencies
pip install apscheduler redis psycopg2-binary

# Database setup
# Run the SQL schema at the bottom of module_8_nudge_scheduler.py
```

## 🚀 Quick Start

### 1. Initialize and Start

```python
from module_8_nudge_scheduler import NudgeScheduler

scheduler = NudgeScheduler()

# Set callback for sending messages
async def send_to_user(user_id: str, message: dict):
    # Your LINE Gateway push message logic
    await line_gateway.push_message(user_id, message)

scheduler.set_send_callback(send_to_user)

# Start scheduler
scheduler.start_scheduler()
```

### 2. Daily Verse

```python
# Get verse for today
verse = scheduler._get_verse_for_today()

print(verse)
# {
#     "reference": "ยอห์น 3:16",
#     "content": "เพราะว่าพระเจ้าทรงรักโลก...",
#     "theme": "love"
# }
```

### 3. Update User Activity

```python
# Call this whenever user interacts
scheduler.update_user_activity("user_123")

# This updates:
# - last_interaction timestamp
# - streak_days (if within 48 hours)
```

## 📅 Scheduled Jobs

| Time | Job | Description |
|------|-----|-------------|
| 08:00 | `daily_verse` | ส่งข้อพระคัมภีร์ให้ users ที่ opt-in |
| 09:00 | `check_inactive` | ตรวจสอบและทัก users ที่ inactive |
| 10:00 | `streak_reminders` | ส่งข้อความ celebrate streak |

## 📊 Inactive User Intervals

ตาม HEARTBEAT.md:

| Days | Message Type | Content |
|------|--------------|---------|
| 7 | ทักทายเบาๆ | "แวะมาส่งกำลังใจ..." |
| 14 | เป็นห่วง | "อุ่นใจยังอยู่ตรงนี้..." (พร้อมคลิป) |
| 30 | กระตุ้น | "คุณพี่คะ อุ่นใจยังรออยู่..." (พร้อมควิซ) |

## 💬 Nudge Templates

### Daily Verse

```
🌅 ข้อพระคัมภีร์ประจำวัน

"เพราะว่าพระเจ้าทรงรักโลก..."

— ยอห์น 3:16

ขอให้วันนี้เป็นวันที่ดีนะคะ 💙
```

### 7 Days Inactive

```
แวะมาส่งกำลังใจให้ในเช้าวันใหม่นะคะ 💙 
อุ่นใจคิดถึงคุณพี่
```

### 14 Days Inactive

```
อุ่นใจยังอยู่ตรงนี้เสมอนะคะ 💙 
คิดถึงคุณพี่จัง แวะมาคุยกันได้นะคะ
```

### Streak Milestone (7, 14, 21... days)

```
🔥 คุณพี่เข้ามา 7 วันติดแล้ว! 
เก่งมากค่ะ มารักษาสถิติกันต่อนะคะ
```

## 🗃️ Database Schema

```sql
-- User nudge states
CREATE TABLE user_nudge_states (
    user_id VARCHAR(255) PRIMARY KEY,
    last_interaction TIMESTAMP,
    last_nudge_sent TIMESTAMP,
    last_nudge_type VARCHAR(50),
    nudge_count INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    daily_verse_opt_in BOOLEAN DEFAULT TRUE,
    preferred_time VARCHAR(5) DEFAULT '08:00',
    timezone VARCHAR(50) DEFAULT 'Asia/Bangkok',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Nudge history
CREATE TABLE nudge_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    nudge_type VARCHAR(50) NOT NULL,
    content TEXT,
    sent_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_nudge_states_interaction ON user_nudge_states(last_interaction);
CREATE INDEX idx_nudge_history_user ON nudge_history(user_id);
```

## 📚 API Reference

### start_scheduler()

เริ่มต้น scheduler พร้อม jobs ที่กำหนดไว้

```python
scheduler.start_scheduler()
# Jobs: daily_verse (08:00), check_inactive (09:00), streak_reminders (10:00)
```

### stop_scheduler()

หยุด scheduler

```python
scheduler.stop_scheduler()
```

### update_user_activity(user_id)

อัปเดตว่า user มี interaction (ควรเรียกทุกครั้งที่ user ทักมา)

```python
scheduler.update_user_activity("user_123")
# Updates: last_interaction, streak_days
```

### send_manual_nudge(user_id, nudge_type, custom_message)

ส่ง nudge แบบ manual (สำหรับ admin)

```python
from module_8_nudge_scheduler import NudgeType

await scheduler.send_manual_nudge(
    user_id="user_123",
    nudge_type=NudgeType.SPECIAL_EVENT,
    custom_message="🎉 สุขสันต์วันเกิดค่ะ!"
)
```

### get_health()

ดูสถานะ scheduler

```python
health = scheduler.get_health()
print(health)
# {
#     "status": "running",
#     "jobs": ["daily_verse", "check_inactive", "streak_reminders"],
#     "daily_verses": 5,
#     "inactive_intervals": [7, 14, 30]
# }
```

## 🔗 Integration with Other Modules

### With LINE Gateway (Module 4)

```python
from module_8_nudge_scheduler import NudgeScheduler
from module_4_line_gateway import LineGateway

line_gateway = LineGateway()
scheduler = NudgeScheduler()

# Connect them
async def send_push(user_id: str, message: dict):
    await line_gateway.push_message(user_id, {
        "type": message["type"],
        "content": message["content"]
    })

scheduler.set_send_callback(send_push)
scheduler.start_scheduler()
```

### With Main Orchestrator (Module 3)

```python
# In orchestrator, after processing message
class MainOrchestrator:
    async def process_message(self, user_id, message, session):
        # Process message...
        
        # Update nudge scheduler
        self.nudge_scheduler.update_user_activity(user_id)
        
        return response
```

## 📖 Daily Verse Collection

มีข้อพระคัมภีร์พร้อมใช้ 5 ข้อ (วน循环):

| Day | Reference | Theme |
|-----|-----------|-------|
| 1 | ยอห์น 3:16 | love |
| 2 | ฟีลิปปี 4:13 | strength |
| 3 | ยอห์น 14:27 | peace |
| 4 | โรม 8:28 | hope |
| 5 | สดุดี 23:1 | provision |

เพิ่มได้ใน `DAILY_VERSES` list

## 🧪 Testing

```bash
# Run built-in tests
python module_8_nudge_scheduler.py
```

Expected output:
```
======================================================================
🔔 Nudge Scheduler Test
======================================================================

📅 Daily Verse for Today:
   ยอห์น 3:16: เพราะว่าพระเจ้าทรงรักโลก...

📨 Sample Nudge Messages:

   inactive_7_days:
   → แวะมาส่งกำลังใจ...

   inactive_14_days:
   → อุ่นใจยังอยู่ตรงนี้...

   streak_reminder:
   → 🔥 คุณพี่เข้ามา...

🏥 Health Check:
   Status: stopped
   Daily Verses: 5
   Inactive Intervals: [7, 14, 30]
```

## ⚙️ Configuration

### Environment Variables

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=unjai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword

REDIS_HOST=localhost
REDIS_PORT=6379
```

### Custom Schedule

```python
from apscheduler.triggers.cron import CronTrigger

# Add custom job
scheduler.scheduler.add_job(
    my_custom_function,
    CronTrigger(hour=20, minute=0),  # 8 PM
    id="evening_nudge",
    replace_existing=True
)
```

## 👥 Agents ที่เกี่ยวข้อง

| Agent | บทบาทใน Module นี้ |
|-------|-------------------|
| **CCO (Community Care Officer)** | จัดการ nudges รายวัน |
| **Passive Watcher (Persona 6)** | Default persona สำหรับ nudges |

## 🔮 Future Improvements

- [ ] A/B testing for nudge messages
- [ ] Personalized verse selection based on user mood
- [ ] Timezone-aware scheduling
- [ ] Birthday nudges
- [ ] Seasonal/event-based nudges
- [ ] Nudge effectiveness analytics

## 📚 Dependencies

```
apscheduler>=3.10.0
redis>=5.0.0
psycopg2-binary>=2.9.9
```
