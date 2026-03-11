"""
Nudge Scheduler Service Entry Point
"""
import os
import sys
import asyncio

# เพิ่ม path เพื่อหาโมดูลใน /app/modules
sys.path.insert(0, '/app/modules')

from module_8_nudge_scheduler import NudgeScheduler

async def main():
    try:
        scheduler = NudgeScheduler()
        
        # ตรวจสอบว่ามีเมธอด setup_default_jobs หรือไม่ก่อนเรียกใช้
        if hasattr(scheduler, 'setup_default_jobs'):
            scheduler.setup_default_jobs()
            print("🚀 Nudge Scheduler: Default jobs configured.")
        else:
            print("⚠️ Warning: setup_default_jobs not found in NudgeScheduler. Skipping...")
        
        print("🚀 Nudge Scheduler started")
        print("⏰ Jobs configured:")
        print("   - Daily verse: 08:00")
        print("   - Inactive check: 09:00")
        print("   - Streak reminder: 10:00")
        
        # วนลูปเพื่อให้ Service ทำงานต่อไป
        while True:
            await asyncio.sleep(60)
            
    except Exception as e:
        print(f"❌ Critical Error in Nudge Scheduler: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping scheduler...")