# Module 5: Smart Coin Manager (The Reward System)

## 📚 Overview

Module นี้เป็น **"ระบบเหรียญรางวัล"** ของ Nong Unjai AI รับผิดชอบ:
- **Balance Management** - จัดการยอด Smart Coins ของผู้ใช้
- **Transaction History** - บันทึกประวัติการรับ/ใช้เหรียญ
- **Reward Distribution** - ให้รางวัลตามกิจกรรม
- **Daily Limits** - จำกัดการรับเหรียญต่อวัน (200 coins)
- **Daily Login Bonus** - รางวัลเข้าสู่ระบบรายวัน
- **Integration** - เชื่อมต่อกับ Quiz และ Video watching

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Smart Coin Manager              │
├─────────────────────────────────────────┤
│  PostgreSQL          Redis             │
│  • Balances          • Daily login     │
│  • Transactions        tracking        │
│  • History                             │
└─────────────────────────────────────────┘
              ↑
    ┌─────────┴─────────┐
    ↓                   ↓
Quiz Complete      Video Watched
    ↓                   ↓
 +20 coins          +10 coins
```

## 📦 Installation

```bash
# Dependencies (already in requirements.txt)
pip install psycopg2-binary redis

# Database setup
# Run SQL schema in your PostgreSQL:
# See SQL Schema section below
```

## 🚀 Quick Start

### 1. Initialize

```python
from module_5_smart_coin import SmartCoinManager, RewardSource

manager = SmartCoinManager()
```

### 2. Check Balance

```python
balance = manager.get_balance("user_123")

print(f"💰 Balance: {balance.balance}")
print(f"📊 Total Earned: {balance.total_earned}")
print(f"🔥 Streak: {balance.streak_days} days")
```

### 3. Earn Coins

```python
# User completed quiz
success, amount, message = manager.earn_coins(
    user_id="user_123",
    source=RewardSource.COMPLETE_QUIZ,
    description="ตอบควิถูก",
    quiz_id="quiz_001"
)

print(message)  # ได้รับ 20 Smart Coins! 🪙
```

### 4. Daily Login

```python
# Check daily login bonus
is_new_day, amount = manager.check_daily_reward("user_123")

if is_new_day:
    print(f"ยินดีต้อนรับ! ได้รับ {amount} coins")
else:
    print("รับรางวัลวันนี้แล้ว กลับมาพรุ่งนี้นะ!")
```

## 📊 Reward Rates

ตาม TOOLS.md Phase 4:

| Activity | Coins | Source |
|----------|-------|--------|
| ดูวิดีโอจบ | 10 | `WATCH_VIDEO` |
| ทำควิซผ่าน | 20 | `COMPLETE_QUIZ` |
| แชร์เนื้อหา | 15 | `SHARE_CONTENT` |
| เข้าสู่ระบบรายวัน | 5 | `DAILY_LOGIN` |
| Streak Bonus | 50 | `STREAK_BONUS` |
| แนะนำเพื่อน | 100 | `REFERRAL` |
| Event พิเศษ | 30 | `SPECIAL_EVENT` |

## 📋 Database Schema

### PostgreSQL Tables

```sql
-- User balances
CREATE TABLE user_coin_balances (
    user_id VARCHAR(255) PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    total_earned INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0,
    total_donated INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    last_login TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Transaction history
CREATE TABLE coin_transactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    amount INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,  -- earn, spend, donate
    source VARCHAR(50),                      -- watch_video, complete_quiz, etc.
    description TEXT,
    quiz_id VARCHAR(255),
    video_id VARCHAR(255),
    balance_after INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_transactions_user ON coin_transactions(user_id);
CREATE INDEX idx_transactions_date ON coin_transactions(created_at);
```

## 💰 API Reference

### get_balance(user_id: str) → UserCoinBalance

ดึงข้อมูลยอดเหรียญของผู้ใช้

```python
balance = manager.get_balance("user_123")
print(balance.balance)        # 150
print(balance.total_earned)   # 500
print(balance.streak_days)    # 5
```

### earn_coins(user_id, source, description, quiz_id, video_id) → Tuple[bool, int, str]

ให้รางวัลเหรียญ

```python
success, amount, message = manager.earn_coins(
    user_id="user_123",
    source=RewardSource.WATCH_VIDEO,
    description="ดูคลิปจบ",
    video_id="vid_001"
)

# Returns: (True, 10, "ได้รับ 10 Smart Coins! 🪙")
```

### spend_coins(user_id, amount, description) → Tuple[bool, int, str]

ใช้เหรียญ

```python
success, amount, message = manager.spend_coins(
    user_id="user_123",
    amount=50,
    description="แลกของรางวัล"
)

# Returns: (True, 50, "ใช้ 50 Smart Coins")
# Or: (False, 0, "ยอด Smart Coins ไม่พอ")
```

### get_transaction_history(user_id, limit) → List[Dict]

ดูประวัติธุรกรรม

```python
history = manager.get_transaction_history("user_123", limit=10)

for tx in history:
    print(f"{tx['created_at']}: {tx['amount']} - {tx['description']}")
```

### get_daily_stats(user_id) → Dict

ดูสถิติรายวัน

```python
stats = manager.get_daily_stats("user_123")

print(f"วันนี้ได้รับ: {stats['total_earned']}/{stats['daily_limit']}")
print(f"เหลือ: {stats['remaining']} coins")
print(f"จากวิดีโอ: {stats['video_earned']}")
print(f"จากควิซ: {stats['quiz_earned']}")
```

### check_daily_reward(user_id) → Tuple[bool, int]

ตรวจสอบและให้รางวัลเข้าสู่ระบบรายวัน

```python
is_new, amount = manager.check_daily_reward("user_123")

if is_new:
    print(f"🎉 ยินดีต้อนรับ! ได้รับ {amount} coins")
else:
    print("⏰ รับรางวัลวันนี้แล้ว")
```

## 🔄 Integration with Other Modules

### With Orchestrator (Module 3)

```python
async def handle_quiz_complete(user_id, quiz_id, is_correct):
    if is_correct:
        success, amount, msg = coin_manager.earn_coins(
            user_id=user_id,
            source=RewardSource.COMPLETE_QUIZ,
            description="ตอบควิซถูกต้อง",
            quiz_id=quiz_id
        )
        
        return {
            "type": "text",
            "content": f"🎉 ถูกต้อง! {msg}\nได้รับเพิ่ม {amount} coins!"
        }
```

### With LINE Gateway (Module 4)

```python
# Send coin balance card
balance = coin_manager.get_balance(user_id)

flex_content = flex_builder.create_progress_card(
    coins=balance.balance,
    r_score=session.r_score,
    circle_level=session.current_circle
)
```

## 📊 Daily Limit System

```python
# Daily limit: 200 coins
# Tracked per source:
# - watch_video: max contribution
# - complete_quiz: max contribution
# - share_content: max contribution

stats = manager.get_daily_stats("user_123")
# {
#     "date": "2024-01-15",
#     "video_earned": 30,      # 3 videos × 10
#     "quiz_earned": 40,       # 2 quizzes × 20
#     "share_earned": 15,      # 1 share × 15
#     "total_earned": 85,
#     "daily_limit": 200,
#     "remaining": 115
# }
```

## 🧪 Testing

```bash
# Run built-in tests
python module_5_smart_coin.py
```

Expected output:
```
======================================================================
🪙 Smart Coin Manager Test
======================================================================

💰 Reward Rates:
   watch_video: 10 coins
   complete_quiz: 20 coins
   share_content: 15 coins
   daily_login: 5 coins
   streak_bonus: 50 coins
   referral: 100 coins
   special_event: 30 coins

🏥 Health Check:
   Status: healthy
   Daily Limit: 200

✅ Smart Coin Manager initialized successfully!
```

## 🛠️ Configuration

### Environment Variables

```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=unjai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Custom Reward Rates

```python
from module_5_smart_coin import SmartCoinManager, RewardSource

manager = SmartCoinManager()

# Override rates
manager.REWARD_RATES[RewardSource.WATCH_VIDEO] = 15
manager.REWARD_RATES[RewardSource.COMPLETE_QUIZ] = 25
```

## 👥 Agents ที่เกี่ยวข้อง

| Agent | บทบาทใน Module นี้ |
|-------|-------------------|
| **Reward Manager** | ให้รางวัล Smart Coins |
| **Insights Analyst** | ดูสถิติการใช้งาน |

## 📈 Future Improvements

- [ ] Shop/Redemption system
- [ ] Donation to charity
- [ ] Leaderboards
- [ ] Streak recovery
- [ ] Seasonal events
- [ ] Referral tracking

## 📚 Dependencies

```
psycopg2-binary>=2.9.9
redis>=5.0.0
```
