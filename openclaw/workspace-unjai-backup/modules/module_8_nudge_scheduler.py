"""
Module 8: Nudge Scheduler (The Engagement Keeper)
Nong Unjai AI System

This module handles proactive user engagement:
- Scheduled nudges (7, 14, 30 days inactive)
- Daily verse delivery
- Streak reminders
- Personalized re-engagement messages
- Cron-based scheduling

Tech Stack:
- APScheduler (Cron jobs)
- Redis (Schedule tracking)
- PostgreSQL (User activity log)
"""

import os
import random
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import httpx
import redis
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NudgeType(Enum):
    """Types of nudges"""
    DAILY_VERSE = "daily_verse"
    INACTIVE_7_DAYS = "inactive_7_days"
    INACTIVE_14_DAYS = "inactive_14_days"
    INACTIVE_30_DAYS = "inactive_30_days"
    STREAK_REMINDER = "streak_reminder"
    BIRTHDAY = "birthday"
    SPECIAL_EVENT = "special_event"
    CIRCLE_PROMOTION = "circle_promotion"


class NudgePriority(Enum):
    """Priority levels for nudges"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class NudgeMessage:
    """A nudge message template"""
    id: str
    nudge_type: NudgeType
    content: str
    persona: int = 6  # Default: Watcher
    priority: NudgePriority = NudgePriority.MEDIUM
    conditions: Dict = None
    flex_content: Optional[Dict] = None
    quick_replies: Optional[List] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}


@dataclass
class UserNudgeState:
    """User's nudge state"""
    user_id: str
    last_interaction: datetime
    last_nudge_sent: Optional[datetime] = None
    last_nudge_type: Optional[str] = None
    nudge_count: int = 0
    streak_days: int = 0
    daily_verse_opt_in: bool = True
    preferred_time: str = "08:00"  # HH:MM
    timezone: str = "Asia/Bangkok"
    
    def days_inactive(self) -> int:
        """Calculate days since last interaction"""
        return (datetime.now() - self.last_interaction).days
    
    def can_send_nudge(self, min_hours: int = 24) -> bool:
        """Check if enough time has passed since last nudge"""
        if not self.last_nudge_sent:
            return True
        hours_since = (datetime.now() - self.last_nudge_sent).total_seconds() / 3600
        return hours_since >= min_hours


class NudgeScheduler:
    """
    Main Nudge Scheduler - handles all proactive messaging
    """
    
    # Nudge intervals (days)
    INACTIVE_INTERVALS = [7, 14, 30]
    
    # Daily verse templates
    DAILY_VERSES = [
        {
            "reference": "ยอห์น 3:16",
            "content": "เพราะว่าพระเจ้าทรงรักโลก...",
            "theme": "love"
        },
        {
            "reference": "ฟีลิปปี 4:13",
            "content": "ข้าพเจ้าทำได้ทุกสิ่ง...",
            "theme": "strength"
        },
        {
            "reference": "ยอห์น 14:27",
            "content": "สันติสุขที่เรามอบให้แก่ท่าน...",
            "theme": "peace"
        },
        {
            "reference": "โรม 8:28",
            "content": "เรารู้ว่าพระเจ้าทรงช่วย...",
            "theme": "hope"
        },
        {
            "reference": "สดุดี 23:1",
            "content": "พระเยโฮวาห์ทรงเลี้ยงดูข้าพเจ้า...",
            "theme": "provision"
        }
    ]
    
    # Nudge message templates
    NUDGE_TEMPLATES = {
        NudgeType.INACTIVE_7_DAYS: [
            {
                "content": "แวะมาส่งกำลังใจให้ในเช้าวันใหม่นะคะ 💙 อุ่นใจคิดถึงคุณพี่",
                "persona": 6
            },
            {
                "content": "สวัสดีค่ะคุณพี่! วันนี้เป็นยังไงบ้าง? อุ่นใจอยู่ตรงนี้เสมอค่ะ",
                "persona": 6
            }
        ],
        NudgeType.INACTIVE_14_DAYS: [
            {
                "content": "อุ่นใจยังอยู่ตรงนี้เสมอนะคะ 💙 คิดถึงคุณพี่จัง แวะมาคุยกันได้นะคะ",
                "persona": 6,
                "with_video": True
            },
            {
                "content": "หายไปนานเลยนะคะ คุณพี่สบายดีไหมคะ? อุ่นใจเป็นห่วงนะคะ",
                "persona": 2
            }
        ],
        NudgeType.INACTIVE_30_DAYS: [
            {
                "content": "คุณพี่คะ อุ่นใจยังรออยู่ตรงนี้เสมอนะคะ 💙 อยากรู้ว่าคุณพี่เป็นอย่างไรบ้าง?",
                "persona": 2,
                "with_quiz": True
            }
        ],
        NudgeType.STREAK_REMINDER: [
            {
                "content": "🔥 คุณพี่เข้ามา {streak} วันติดแล้ว! เก่งมากค่ะ มารักษาสถิติกันต่อนะคะ",
                "persona": 11
            }
        ]
    }
    
    def __init__(self):
        # Database
        self.db_host = os.getenv("POSTGRES_HOST", "localhost")
        self.db_port = int(os.getenv("POSTGRES_PORT", 5432))
        self.db_name = os.getenv("POSTGRES_DB", "unjai")
        self.db_user = os.getenv("POSTGRES_USER", "postgres")
        self.db_password = os.getenv("POSTGRES_PASSWORD", "")
        
        # Redis
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=3,  # Use DB 3 for nudges
            decode_responses=True
        )
        
        # Scheduler
        self.scheduler = AsyncIOScheduler()
        
        # Callback for sending messages (to be set)
        self.send_callback: Optional[Callable] = None
        
        logger.info("Nudge Scheduler initialized")
    
    def _get_db_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
    
    def start_scheduler(self):
        """Start the scheduler"""
        # Daily verse at 8:00 AM
        self.scheduler.add_job(
            self._send_daily_verses,
            CronTrigger(hour=8, minute=0),
            id="daily_verse",
            replace_existing=True
        )
        
        # Check inactive users at 9:00 AM
        self.scheduler.add_job(
            self._check_inactive_users,
            CronTrigger(hour=9, minute=0),
            id="check_inactive",
            replace_existing=True
        )
        
        # Check streak reminders at 10:00 AM
        self.scheduler.add_job(
            self._send_streak_reminders,
            CronTrigger(hour=10, minute=0),
            id="streak_reminders",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Scheduler started with jobs: daily_verse, check_inactive, streak_reminders")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    # Daily Verse
    
    async def _send_daily_verses(self):
        """Send daily verses to opted-in users"""
        logger.info("Sending daily verses...")
        
        try:
            # Get users who opted in
            users = self._get_daily_verse_users()
            
            # Select verse for today
            verse = self._get_verse_for_today()
            
            for user in users:
                message = self._build_daily_verse_message(verse)
                
                if self.send_callback:
                    await self.send_callback(user["user_id"], message)
                
                logger.info(f"Sent daily verse to {user['user_id']}")
                
        except Exception as e:
            logger.error(f"Error sending daily verses: {e}")
    
    def _get_verse_for_today(self) -> Dict:
        """Get verse for today (deterministic based on date)"""
        day_of_year = datetime.now().timetuple().tm_yday
        index = day_of_year % len(self.DAILY_VERSES)
        return self.DAILY_VERSES[index]
    
    def _build_daily_verse_message(self, verse: Dict) -> Dict:
        """Build daily verse message"""
        return {
            "type": "text",
            "content": (
                f"🌅 ข้อพระคัมภีร์ประจำวัน\n\n"
                f"\"{verse['content']}\"\n\n"
                f"— {verse['reference']}\n\n"
                f"ขอให้วันนี้เป็นวันที่ดีนะคะ 💙"
            ),
            "persona": 6
        }
    
    # Inactive User Nudges
    
    async def _check_inactive_users(self):
        """Check and nudge inactive users"""
        logger.info("Checking inactive users...")
        
        try:
            for days in self.INACTIVE_INTERVALS:
                users = self._get_inactive_users(days)
                
                for user in users:
                    if user.can_send_nudge():
                        nudge_type = self._get_nudge_type_for_days(days)
                        message = self._build_nudge_message(nudge_type, user)
                        
                        if self.send_callback:
                            await self.send_callback(user.user_id, message)
                        
                        self._update_nudge_sent(user.user_id, nudge_type)
                        logger.info(f"Sent {nudge_type.value} to {user.user_id}")
                        
        except Exception as e:
            logger.error(f"Error checking inactive users: {e}")
    
    def _get_inactive_users(self, days: int) -> List[UserNudgeState]:
        """Get users inactive for specific days"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Find users with last interaction exactly N days ago
            cursor.execute("""
                SELECT user_id, last_interaction, last_nudge_sent, last_nudge_type,
                       nudge_count, streak_days, daily_verse_opt_in
                FROM user_nudge_states
                WHERE DATE(last_interaction) = DATE(NOW() - INTERVAL '%s days')
                AND (last_nudge_sent IS NULL OR DATE(last_nudge_sent) < DATE(NOW() - INTERVAL '1 day'))
            """, (days,))
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            users = []
            for row in rows:
                users.append(UserNudgeState(
                    user_id=row["user_id"],
                    last_interaction=row["last_interaction"],
                    last_nudge_sent=row["last_nudge_sent"],
                    last_nudge_type=row["last_nudge_type"],
                    nudge_count=row["nudge_count"],
                    streak_days=row["streak_days"],
                    daily_verse_opt_in=row["daily_verse_opt_in"]
                ))
            
            return users
            
        except Exception as e:
            logger.error(f"Error getting inactive users: {e}")
            return []
    
    def _get_nudge_type_for_days(self, days: int) -> NudgeType:
        """Get nudge type for specific days"""
        mapping = {
            7: NudgeType.INACTIVE_7_DAYS,
            14: NudgeType.INACTIVE_14_DAYS,
            30: NudgeType.INACTIVE_30_DAYS
        }
        return mapping.get(days, NudgeType.INACTIVE_7_DAYS)
    
    def _build_nudge_message(self, nudge_type: NudgeType, user: UserNudgeState) -> Dict:
        """Build nudge message"""
        templates = self.NUDGE_TEMPLATES.get(nudge_type, [])
        
        if not templates:
            return {
                "type": "text",
                "content": "คิดถึงคุณพี่นะคะ 💙",
                "persona": 6
            }
        
        template = random.choice(templates)
        content = template["content"]
        
        # Format with user data
        content = content.format(streak=user.streak_days)
        
        return {
            "type": "text",
            "content": content,
            "persona": template.get("persona", 6),
            "with_video": template.get("with_video", False),
            "with_quiz": template.get("with_quiz", False)
        }
    
    # Streak Reminders
    
    async def _send_streak_reminders(self):
        """Send streak reminders to active users"""
        logger.info("Sending streak reminders...")
        
        try:
            users = self._get_streak_users()
            
            for user in users:
                if user.streak_days > 0 and user.streak_days % 7 == 0:
                    # Milestone streak (7, 14, 21, ...)
                    message = self._build_streak_message(user)
                    
                    if self.send_callback:
                        await self.send_callback(user.user_id, message)
                    
                    logger.info(f"Sent streak reminder to {user.user_id} ({user.streak_days} days)")
                    
        except Exception as e:
            logger.error(f"Error sending streak reminders: {e}")
    
    def _get_streak_users(self) -> List[UserNudgeState]:
        """Get users with active streaks"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT user_id, last_interaction, streak_days
                FROM user_nudge_states
                WHERE streak_days > 0
                AND last_interaction >= NOW() - INTERVAL '1 day'
            """)
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            users = []
            for row in rows:
                users.append(UserNudgeState(
                    user_id=row["user_id"],
                    last_interaction=row["last_interaction"],
                    streak_days=row["streak_days"]
                ))
            
            return users
            
        except Exception as e:
            logger.error(f"Error getting streak users: {e}")
            return []
    
    def _build_streak_message(self, user: UserNudgeState) -> Dict:
        """Build streak milestone message"""
        templates = self.NUDGE_TEMPLATES.get(NudgeType.STREAK_REMINDER, [])
        template = templates[0] if templates else {"content": "เก่งมากค่ะ!", "persona": 11}
        
        content = template["content"].format(streak=user.streak_days)
        
        return {
            "type": "text",
            "content": content,
            "persona": template.get("persona", 11)
        }
    
    # User State Management
    
    def update_user_activity(self, user_id: str):
        """Update user activity timestamp"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Check last interaction for streak calculation
            cursor.execute("""
                SELECT last_interaction, streak_days
                FROM user_nudge_states
                WHERE user_id = %s
            """, (user_id,))
            
            row = cursor.fetchone()
            
            if row:
                last_interaction, streak = row
                # Check if continuing streak (within 48 hours)
                if last_interaction and (datetime.now() - last_interaction) < timedelta(hours=48):
                    new_streak = streak + 1
                else:
                    new_streak = 1  # Reset streak
                
                cursor.execute("""
                    UPDATE user_nudge_states
                    SET last_interaction = NOW(),
                        streak_days = %s,
                        updated_at = NOW()
                    WHERE user_id = %s
                """, (new_streak, user_id))
            else:
                # New user
                cursor.execute("""
                    INSERT INTO user_nudge_states
                    (user_id, last_interaction, streak_days, created_at, updated_at)
                    VALUES (%s, NOW(), 1, NOW(), NOW())
                """, (user_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
    
    def _update_nudge_sent(self, user_id: str, nudge_type: NudgeType):
        """Record that nudge was sent"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE user_nudge_states
                SET last_nudge_sent = NOW(),
                    last_nudge_type = %s,
                    nudge_count = nudge_count + 1,
                    updated_at = NOW()
                WHERE user_id = %s
            """, (nudge_type.value, user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating nudge sent: {e}")
    
    def _get_daily_verse_users(self) -> List[Dict]:
        """Get users opted in for daily verses"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT user_id, preferred_time
                FROM user_nudge_states
                WHERE daily_verse_opt_in = TRUE
            """)
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting daily verse users: {e}")
            return []
    
    # Manual nudges
    
    async def send_manual_nudge(self, user_id: str, nudge_type: NudgeType, 
                                 custom_message: str = None) -> bool:
        """Send a manual nudge to specific user"""
        try:
            user = UserNudgeState(
                user_id=user_id,
                last_interaction=datetime.now() - timedelta(days=7)
            )
            
            if custom_message:
                message = {
                    "type": "text",
                    "content": custom_message,
                    "persona": 6
                }
            else:
                message = self._build_nudge_message(nudge_type, user)
            
            if self.send_callback:
                await self.send_callback(user_id, message)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending manual nudge: {e}")
            return False
    
    # Callback setter
    
    def set_send_callback(self, callback: Callable):
        """Set callback for sending messages"""
        self.send_callback = callback
    
    def get_health(self) -> Dict:
        """Get scheduler health"""
        jobs = self.scheduler.get_jobs()
        
        return {
            "status": "running" if self.scheduler.running else "stopped",
            "jobs": [job.id for job in jobs],
            "daily_verses": len(self.DAILY_VERSES),
            "inactive_intervals": self.INACTIVE_INTERVALS,
            "timestamp": datetime.now().isoformat()
        }


# Database Schema (for reference)
"""
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

-- Indexes
CREATE INDEX idx_nudge_states_interaction ON user_nudge_states(last_interaction);
CREATE INDEX idx_nudge_history_user ON nudge_history(user_id);
"""


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_scheduler():
        print("=" * 70)
        print("🔔 Nudge Scheduler Test")
        print("=" * 70)
        
        scheduler = NudgeScheduler()
        
        # Mock send callback
        async def mock_send(user_id: str, message: Dict):
            print(f"\n📤 To {user_id}:")
            print(f"   {message['content'][:60]}...")
        
        scheduler.set_send_callback(mock_send)
        
        print("\n📅 Daily Verse for Today:")
        verse = scheduler._get_verse_for_today()
        print(f"   {verse['reference']}: {verse['content']}")
        
        print("\n📨 Sample Nudge Messages:")
        
        from module_8_nudge_scheduler import NudgeType, UserNudgeState
        
        test_states = [
            UserNudgeState(user_id="user_1", last_interaction=datetime.now() - timedelta(days=7)),
            UserNudgeState(user_id="user_2", last_interaction=datetime.now() - timedelta(days=14)),
            UserNudgeState(user_id="user_3", last_interaction=datetime.now() - timedelta(days=3), streak_days=7),
        ]
        
        nudge_types = [NudgeType.INACTIVE_7_DAYS, NudgeType.INACTIVE_14_DAYS, NudgeType.STREAK_REMINDER]
        
        for state, nudge_type in zip(test_states, nudge_types):
            message = scheduler._build_nudge_message(nudge_type, state)
            print(f"\n   {nudge_type.value}:")
            print(f"   → {message['content'][:50]}...")
        
        print("\n🏥 Health Check:")
        health = scheduler.get_health()
        print(f"   Status: {health['status']}")
        print(f"   Daily Verses: {health['daily_verses']}")
        print(f"   Inactive Intervals: {health['inactive_intervals']}")
        
        print("\n" + "=" * 70)
        print("✅ Test completed!")
        print("=" * 70)
    
    asyncio.run(test_scheduler())
