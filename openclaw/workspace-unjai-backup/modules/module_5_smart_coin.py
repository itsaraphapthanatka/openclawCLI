"""
Module 5: Smart Coin Manager (The Reward System)
Nong Unjai AI System

This module handles:
- Smart Coin balance management
- Transaction history
- Reward distribution
- Daily limits enforcement
- Coin redemption/shop
- Integration with quiz completion and video watching
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

import psycopg2
from psycopg2.extras import RealDictCursor
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """Types of coin transactions"""
    EARN = "earn"
    SPEND = "spend"
    REDEEM = "redeem"
    DONATE = "donate"
    BONUS = "bonus"


class RewardSource(Enum):
    """Sources of coin rewards"""
    WATCH_VIDEO = "watch_video"
    COMPLETE_QUIZ = "complete_quiz"
    SHARE_CONTENT = "share_content"
    DAILY_LOGIN = "daily_login"
    STREAK_BONUS = "streak_bonus"
    REFERRAL = "referral"
    SPECIAL_EVENT = "special_event"
    ADMIN_GRANT = "admin_grant"


@dataclass
class CoinTransaction:
    """A single coin transaction"""
    id: Optional[int] = None
    user_id: str = ""
    amount: int = 0
    transaction_type: TransactionType = TransactionType.EARN
    source: Optional[RewardSource] = None
    description: str = ""
    quiz_id: Optional[str] = None
    video_id: Optional[str] = None
    balance_after: int = 0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type.value,
            "source": self.source.value if self.source else None,
            "description": self.description,
            "quiz_id": self.quiz_id,
            "video_id": self.video_id,
            "balance_after": self.balance_after,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class UserCoinBalance:
    """User's coin balance and stats"""
    user_id: str
    balance: int = 0
    total_earned: int = 0
    total_spent: int = 0
    total_donated: int = 0
    streak_days: int = 0
    last_login: Optional[datetime] = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = datetime.now()


class SmartCoinManager:
    """
    Main Smart Coin Manager
    """
    
    # Reward rates from TOOLS.md
    REWARD_RATES = {
        RewardSource.WATCH_VIDEO: 10,
        RewardSource.COMPLETE_QUIZ: 20,
        RewardSource.SHARE_CONTENT: 15,
        RewardSource.DAILY_LOGIN: 5,
        RewardSource.STREAK_BONUS: 50,
        RewardSource.REFERRAL: 100,
        RewardSource.SPECIAL_EVENT: 30,
        RewardSource.ADMIN_GRANT: 0
    }
    
    def __init__(self):
        self.db_host = os.getenv("POSTGRES_HOST", "localhost")
        self.db_port = int(os.getenv("POSTGRES_PORT", 5432))
        self.db_name = os.getenv("POSTGRES_DB", "unjai")
        self.db_user = os.getenv("POSTGRES_USER", "postgres")
        self.db_password = os.getenv("POSTGRES_PASSWORD", "")
        
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=2,
            decode_responses=True
        )
        
        self.daily_limit = 200
        logger.info("Smart Coin Manager initialized")
    
    def _get_db_connection(self):
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
    
    def get_balance(self, user_id: str) -> UserCoinBalance:
        """Get user's coin balance"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM user_coin_balances 
                WHERE user_id = %s
            """, (user_id,))
            
            row = cursor.fetchone()
            
            if row:
                balance = UserCoinBalance(
                    user_id=row["user_id"],
                    balance=row["balance"],
                    total_earned=row["total_earned"],
                    total_spent=row["total_spent"],
                    total_donated=row["total_donated"],
                    streak_days=row["streak_days"],
                    last_login=row["last_login"],
                    updated_at=row["updated_at"]
                )
            else:
                balance = UserCoinBalance(user_id=user_id)
                self._create_balance_record(cursor, conn, balance)
            
            cursor.close()
            conn.close()
            return balance
            
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return UserCoinBalance(user_id=user_id)
    
    def _create_balance_record(self, cursor, conn, balance: UserCoinBalance):
        cursor.execute("""
            INSERT INTO user_coin_balances 
            (user_id, balance, total_earned, total_spent, total_donated, 
             streak_days, last_login, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            balance.user_id, balance.balance, balance.total_earned,
            balance.total_spent, balance.total_donated, balance.streak_days,
            balance.last_login, balance.updated_at
        ))
        conn.commit()
    
    def earn_coins(self, user_id: str, source: RewardSource, 
                   description: str = "", quiz_id: str = None,
                   video_id: str = None) -> Tuple[bool, int, str]:
        """Award coins to user"""
        amount = self.REWARD_RATES.get(source, 0)
        
        if amount <= 0:
            return False, 0, "Invalid reward source"
        
        try:
            new_balance = self._update_balance(user_id, amount, TransactionType.EARN)
            
            transaction = CoinTransaction(
                user_id=user_id,
                amount=amount,
                transaction_type=TransactionType.EARN,
                source=source,
                description=description,
                quiz_id=quiz_id,
                video_id=video_id,
                balance_after=new_balance
            )
            self._record_transaction(transaction)
            
            logger.info(f"Awarded {amount} coins to {user_id} from {source.value}")
            return True, amount, f"ได้รับ {amount} Smart Coins! 🪙"
            
        except Exception as e:
            logger.error(f"Error awarding coins: {e}")
            return False, 0, str(e)
    
    def _update_balance(self, user_id: str, delta: int, 
                        transaction_type: TransactionType) -> int:
        """Update balance and return new balance"""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT balance FROM user_coin_balances WHERE user_id = %s
        """, (user_id,))
        
        row = cursor.fetchone()
        if not row:
            current_balance = 0
            cursor.execute("""
                INSERT INTO user_coin_balances (user_id, balance, updated_at)
                VALUES (%s, 0, NOW())
            """, (user_id,))
        else:
            current_balance = row[0]
        
        new_balance = current_balance + delta
        
        if new_balance < 0:
            raise ValueError("Insufficient balance")
        
        cursor.execute("""
            UPDATE user_coin_balances 
            SET balance = %s,
                total_earned = CASE WHEN %s > 0 THEN total_earned + %s ELSE total_earned END,
                total_spent = CASE WHEN %s < 0 THEN total_spent + ABS(%s) ELSE total_spent END,
                updated_at = NOW()
            WHERE user_id = %s
        """, (new_balance, delta, delta, delta, delta, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return new_balance
    
    def _record_transaction(self, transaction: CoinTransaction):
        """Record transaction to database"""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO coin_transactions 
            (user_id, amount, transaction_type, source, description, 
             quiz_id, video_id, balance_after, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            transaction.user_id,
            transaction.amount,
            transaction.transaction_type.value,
            transaction.source.value if transaction.source else None,
            transaction.description,
            transaction.quiz_id,
            transaction.video_id,
            transaction.balance_after,
            transaction.created_at
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def spend_coins(self, user_id: str, amount: int, 
                    description: str = "") -> Tuple[bool, int, str]:
        """Spend coins"""
        if amount <= 0:
            return False, 0, "Amount must be positive"
        
        try:
            new_balance = self._update_balance(user_id, -amount, TransactionType.SPEND)
            
            transaction = CoinTransaction(
                user_id=user_id,
                amount=-amount,
                transaction_type=TransactionType.SPEND,
                description=description,
                balance_after=new_balance
            )
            self._record_transaction(transaction)
            
            return True, amount, f"ใช้ {amount} Smart Coins"
            
        except ValueError:
            return False, 0, "ยอด Smart Coins ไม่พอ"
        except Exception as e:
            logger.error(f"Error spending coins: {e}")
            return False, 0, str(e)
    
    def get_transaction_history(self, user_id: str, 
                                 limit: int = 20) -> List[Dict]:
        """Get transaction history"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM coin_transactions 
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            return []
    
    def get_daily_stats(self, user_id: str) -> Dict:
        """Get daily earning stats"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN source = 'watch_video' THEN amount ELSE 0 END), 0) as video_earned,
                    COALESCE(SUM(CASE WHEN source = 'complete_quiz' THEN amount ELSE 0 END), 0) as quiz_earned,
                    COALESCE(SUM(CASE WHEN source = 'share_content' THEN amount ELSE 0 END), 0) as share_earned,
                    COALESCE(SUM(amount), 0) as total_earned
                FROM coin_transactions
                WHERE user_id = %s 
                AND transaction_type = 'earn'
                AND DATE(created_at) = %s
            """, (user_id, today))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            video_earned, quiz_earned, share_earned, total = row
            
            return {
                "date": today,
                "video_earned": video_earned,
                "quiz_earned": quiz_earned,
                "share_earned": share_earned,
                "total_earned": total,
                "daily_limit": self.daily_limit,
                "remaining": max(0, self.daily_limit - total)
            }
            
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return {
                "date": today,
                "video_earned": 0,
                "quiz_earned": 0,
                "share_earned": 0,
                "total_earned": 0,
                "daily_limit": self.daily_limit,
                "remaining": self.daily_limit
            }
    
    def check_daily_reward(self, user_id: str) -> Tuple[bool, int]:
        """Check and award daily login bonus"""
        today = datetime.now().strftime("%Y-%m-%d")
        key = f"daily_login:{user_id}:{today}"
        
        # Check if already claimed today
        if self.redis.get(key):
            return False, 0
        
        # Award daily login
        success, amount, _ = self.earn_coins(
            user_id=user_id,
            source=RewardSource.DAILY_LOGIN,
            description="เข้าสู่ระบบรายวัน"
        )
        
        if success:
            # Mark as claimed
            self.redis.setex(key, 86400, "1")
            return True, amount
        
        return False, 0
    
    def get_health(self) -> Dict:
        """Get health status"""
        return {
            "status": "healthy",
            "daily_limit": self.daily_limit,
            "reward_rates": {
                k.value: v for k, v in self.REWARD_RATES.items()
            },
            "timestamp": datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("🪙 Smart Coin Manager Test")
    print("=" * 70)
    
    manager = SmartCoinManager()
    
    print("\n💰 Reward Rates:")
    for source, amount in manager.REWARD_RATES.items():
        print(f"   {source.value}: {amount} coins")
    
    print("\n🏥 Health Check:")
    health = manager.get_health()
    print(f"   Status: {health['status']}")
    print(f"   Daily Limit: {health['daily_limit']}")
    
    print("\n✅ Smart Coin Manager initialized successfully!")
    print("=" * 70)
