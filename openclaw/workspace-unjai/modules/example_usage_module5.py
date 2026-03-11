#!/usr/bin/env python3
"""
Example usage of Module 5: Smart Coin Manager
Nong Unjai AI System
"""

import asyncio
from module_5_smart_coin import SmartCoinManager, RewardSource, TransactionType


def example_1_reward_rates():
    """Example 1: View Reward Rates"""
    print("=" * 70)
    print("Example 1: Reward Rates")
    print("=" * 70)
    
    manager = SmartCoinManager()
    
    print("\n💰 Smart Coin Reward Rates:")
    print("-" * 50)
    
    icons = {
        RewardSource.WATCH_VIDEO: "🎥",
        RewardSource.COMPLETE_QUIZ: "🎯",
        RewardSource.SHARE_CONTENT: "📤",
        RewardSource.DAILY_LOGIN: "📅",
        RewardSource.STREAK_BONUS: "🔥",
        RewardSource.REFERRAL: "👥",
        RewardSource.SPECIAL_EVENT: "🎉",
        RewardSource.ADMIN_GRANT: "👑"
    }
    
    for source, amount in manager.REWARD_RATES.items():
        icon = icons.get(source, "🪙")
        print(f"   {icon} {source.value:20s}: {amount:3d} coins")
    
    print("-" * 50)
    print(f"   📊 Daily Limit: {manager.daily_limit} coins")


def example_2_earn_coins():
    """Example 2: Earn Coins"""
    print("\n" + "=" * 70)
    print("Example 2: Earn Coins")
    print("=" * 70)
    
    manager = SmartCoinManager()
    
    user_id = "user_demo"
    
    # Scenario: User completes various activities
    activities = [
        (RewardSource.WATCH_VIDEO, "ดูคลิปหนุนใจจบ", "vid_001"),
        (RewardSource.COMPLETE_QUIZ, "ตอบควิซถูก 3/3", "quiz_001"),
        (RewardSource.SHARE_CONTENT, "แชร์คลิปให้เพื่อน", None),
    ]
    
    print(f"\n👤 User: {user_id}")
    print("\n🎮 Activities:")
    
    for source, desc, item_id in activities:
        success, amount, message = manager.earn_coins(
            user_id=user_id,
            source=source,
            description=desc,
            video_id=item_id
        )
        
        status = "✅" if success else "❌"
        print(f"   {status} {desc}")
        print(f"      → {message}")


def example_3_check_balance():
    """Example 3: Check Balance"""
    print("\n" + "=" * 70)
    print("Example 3: Check Balance")
    print("=" * 70)
    
    manager = SmartCoinManager()
    
    user_id = "user_demo"
    balance = manager.get_balance(user_id)
    
    print(f"\n💰 Coin Balance for {user_id}:")
    print(f"   🪙 Current: {balance.balance} coins")
    print(f"   📈 Total Earned: {balance.total_earned}")
    print(f"   📉 Total Spent: {balance.total_spent}")
    print(f"   💝 Total Donated: {balance.total_donated}")
    print(f"   🔥 Streak: {balance.streak_days} days")
    
    if balance.last_login:
        print(f"   📅 Last Login: {balance.last_login}")


def example_4_daily_stats():
    """Example 4: Daily Statistics"""
    print("\n" + "=" * 70)
    print("Example 4: Daily Statistics")
    print("=" * 70)
    
    manager = SmartCoinManager()
    
    user_id = "user_demo"
    stats = manager.get_daily_stats(user_id)
    
    print(f"\n📊 Daily Stats for {user_id}:")
    print(f"   📅 Date: {stats['date']}")
    print()
    print(f"   🎥 From Videos:    {stats['video_earned']:3d} coins")
    print(f"   🎯 From Quizzes:   {stats['quiz_earned']:3d} coins")
    print(f"   📤 From Shares:    {stats['share_earned']:3d} coins")
    print("-" * 30)
    print(f"   📈 Total Today:    {stats['total_earned']:3d}/{stats['daily_limit']} coins")
    print(f"   💚 Remaining:      {stats['remaining']:3d} coins")
    
    # Progress bar
    progress = int((stats['total_earned'] / stats['daily_limit']) * 20)
    bar = "█" * progress + "░" * (20 - progress)
    print(f"   [{bar}] {stats['total_earned']}/{stats['daily_limit']}")


def example_5_daily_login():
    """Example 5: Daily Login Bonus"""
    print("\n" + "=" * 70)
    print("Example 5: Daily Login Bonus")
    print("=" * 70)
    
    manager = SmartCoinManager()
    
    user_id = "user_demo"
    
    print(f"\n👤 User: {user_id}")
    print("\n📅 Checking daily login...")
    
    is_new_day, amount = manager.check_daily_reward(user_id)
    
    if is_new_day:
        print(f"   🎉 ยินดีต้อนรับกลับมา!")
        print(f"   🪙 ได้รับรางวัลเข้าสู่ระบบ: {amount} coins")
    else:
        print(f"   ⏰ รับรางวัลวันนี้แล้ว")
        print(f"   🌅 กลับมาพรุ่งนี้เพื่อรับ coins เพิ่ม!")


def example_6_transaction_history():
    """Example 6: Transaction History"""
    print("\n" + "=" * 70)
    print("Example 6: Transaction History")
    print("=" * 70)
    
    manager = SmartCoinManager()
    
    user_id = "user_demo"
    history = manager.get_transaction_history(user_id, limit=10)
    
    print(f"\n📜 Recent Transactions for {user_id}:")
    print("-" * 60)
    
    if history:
        for tx in history:
            icon = "🟢" if tx['amount'] > 0 else "🔴"
            source = tx.get('source', 'unknown')
            print(f"   {icon} {tx['amount']:+4d} | {source:15s} | {tx['description'][:20]:20s}")
    else:
        print("   No transactions yet")


def example_7_spend_coins():
    """Example 7: Spend Coins"""
    print("\n" + "=" * 70)
    print("Example 7: Spend Coins")
    print("=" * 70)
    
    manager = SmartCoinManager()
    
    user_id = "user_demo"
    
    # Check current balance
    balance = manager.get_balance(user_id)
    print(f"\n💰 Current Balance: {balance.balance} coins")
    
    # Try to spend
    spend_amount = 50
    print(f"\n🛒 Trying to spend {spend_amount} coins...")
    
    success, amount, message = manager.spend_coins(
        user_id=user_id,
        amount=spend_amount,
        description="แลกของรางวัล"
    )
    
    if success:
        print(f"   ✅ {message}")
        print(f"   🪙 Remaining: {balance.balance - amount} coins")
    else:
        print(f"   ❌ {message}")


def example_8_integration_scenario():
    """Example 8: Full Integration Scenario"""
    print("\n" + "=" * 70)
    print("Example 8: Full Integration Scenario")
    print("=" * 70)
    
    print("""
🎮 User Journey with Smart Coins:

09:00 - User opens LINE OA
        ↓ check_daily_reward()
        🪙 +5 coins (Daily Login)
        🔥 Streak: 3 days

09:05 - User watches encouragement video
        ↓ earn_coins(WATCH_VIDEO)
        🎥 +10 coins
        Total: 15 coins

09:15 - User completes quiz
        ↓ earn_coins(COMPLETE_QUIZ)
        🎯 +20 coins
        Total: 35 coins

09:20 - User shares video to friend
        ↓ earn_coins(SHARE_CONTENT)
        📤 +15 coins
        Total: 50 coins

12:00 - User checks balance
        ↓ get_balance()
        💰 50 coins available
        📈 50 earned today
        💚 150 remaining daily limit

--- End of Day ---
Daily Stats:
  🎥 Videos: 10 coins
  🎯 Quizzes: 20 coins
  📤 Shares: 15 coins
  📅 Login: 5 coins
  ─────────────────
  Total: 50/200 coins (25%)
    """)


def example_9_health_check():
    """Example 9: System Health"""
    print("\n" + "=" * 70)
    print("Example 9: Health Check")
    print("=" * 70)
    
    manager = SmartCoinManager()
    health = manager.get_health()
    
    print("\n🏥 Smart Coin System Health:")
    print(f"   Status: {health['status']}")
    print(f"   Daily Limit: {health['daily_limit']} coins")
    print(f"   Timestamp: {health['timestamp']}")
    
    print("\n   💰 Active Reward Rates:")
    for source, amount in health['reward_rates'].items():
        if amount > 0:
            print(f"      {source}: {amount}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🪙 Module 5: Smart Coin Manager - Examples")
    print("=" * 70)
    
    try:
        example_1_reward_rates()
        example_2_earn_coins()
        example_3_check_balance()
        example_4_daily_stats()
        example_5_daily_login()
        example_6_transaction_history()
        example_7_spend_coins()
        example_8_integration_scenario()
        example_9_health_check()
        
        print("\n" + "=" * 70)
        print("✅ All examples completed!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
