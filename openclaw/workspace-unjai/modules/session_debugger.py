"""
Debug Session Logger - บันทึกทุก Session ที่มีการถามตอบ
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Ensure debug directory exists
DEBUG_DIR = Path("/home/node/.openclaw/workspace-unjai/debug")
DEBUG_DIR.mkdir(exist_ok=True)

@dataclass
class QARecord:
    """บันทึกการถามตอบแต่ละครั้ง"""
    timestamp: str
    user_id: str
    question: str
    raw_clip_url: str  # URL ดิบจาก Pinecone
    full_clip_url: str  # URL หลังเติม base URL
    score: float
    decision: str  # text_only, video_nudge, video_package
    persona_id: int
    response_type: str

@dataclass
class SessionDebug:
    """ข้อมูล Debug ของแต่ละ Session"""
    session_id: str
    user_id: str
    start_time: str
    last_activity: str
    qa_count: int
    qa_history: List[QARecord]
    
class SessionDebugger:
    """ตัวช่วย Debug Session ทั้งหมด"""
    
    def __init__(self):
        self.base_url = os.getenv("BASE_URL", "https://nongaunjai.febradio.org")
        self.sessions_file = DEBUG_DIR / "sessions_debug.json"
        self.sessions: Dict[str, SessionDebug] = {}
        self.load_sessions()
    
    def load_sessions(self):
        """โหลดข้อมูล sessions จากไฟล์"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for sid, sdata in data.items():
                        qa_history = [QARecord(**qa) for qa in sdata.get('qa_history', [])]
                        self.sessions[sid] = SessionDebug(
                            session_id=sid,
                            user_id=sdata['user_id'],
                            start_time=sdata['start_time'],
                            last_activity=sdata['last_activity'],
                            qa_count=sdata['qa_count'],
                            qa_history=qa_history
                        )
            except Exception as e:
                print(f"⚠️ Error loading sessions: {e}")
    
    def save_sessions(self):
        """บันทึกข้อมูล sessions ลงไฟล์"""
        try:
            data = {}
            for sid, session in self.sessions.items():
                data[sid] = {
                    'session_id': session.session_id,
                    'user_id': session.user_id,
                    'start_time': session.start_time,
                    'last_activity': session.last_activity,
                    'qa_count': session.qa_count,
                    'qa_history': [asdict(qa) for qa in session.qa_history]
                }
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving sessions: {e}")
    
    def log_qa(self, 
               session_id: str,
               user_id: str,
               question: str,
               raw_clip_url: str,
               full_clip_url: str,
               score: float,
               decision: str,
               persona_id: int,
               response_type: str):
        """บันทึกการถามตอบ"""
        now = datetime.now().isoformat()
        
        qa = QARecord(
            timestamp=now,
            user_id=user_id,
            question=question,
            raw_clip_url=raw_clip_url,
            full_clip_url=full_clip_url,
            score=score,
            decision=decision,
            persona_id=persona_id,
            response_type=response_type
        )
        
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionDebug(
                session_id=session_id,
                user_id=user_id,
                start_time=now,
                last_activity=now,
                qa_count=0,
                qa_history=[]
            )
        
        session = self.sessions[session_id]
        session.qa_history.append(qa)
        session.qa_count += 1
        session.last_activity = now
        
        self.save_sessions()
        
        # แสดง log ทันที
        self._print_qa_log(qa, session_id)
    
    def _print_qa_log(self, qa: QARecord, session_id: str):
        """แสดง log การถามตอบ"""
        print("\n" + "="*70)
        print(f"📋 QA Debug Log | Session: {session_id[:8]}... | {qa.timestamp}")
        print("="*70)
        print(f"👤 User: {qa.user_id}")
        print(f"❓ Question: {qa.question[:60]}...")
        print(f"🎯 Decision: {qa.decision} | Persona: {qa.persona_id} | Score: {qa.score:.3f}")
        print(f"📎 Raw URL: {qa.raw_clip_url}")
        print(f"🔗 Full URL: {qa.full_clip_url}")
        print(f"✅ Base URL correct: {qa.full_clip_url.startswith(self.base_url)}")
        print("="*70)
    
    def get_all_sessions(self) -> Dict[str, SessionDebug]:
        """ดึงข้อมูลทุก session"""
        return self.sessions
    
    def get_session_summary(self) -> str:
        """สรุปข้อมูล sessions ทั้งหมด"""
        total_sessions = len(self.sessions)
        total_qa = sum(s.qa_count for s in self.sessions.values())
        
        lines = [
            "\n" + "="*70,
            "📊 Session Debug Summary",
            "="*70,
            f"Total Sessions: {total_sessions}",
            f"Total Q&A: {total_qa}",
            "",
            "Active Sessions:",
        ]
        
        for sid, session in self.sessions.items():
            lines.append(f"  • {sid[:16]}... | User: {session.user_id[:12]}... | "
                        f"QA: {session.qa_count} | Last: {session.last_activity[:19]}")
            # แสดงคำถามล่าสุด
            if session.qa_history:
                last_qa = session.qa_history[-1]
                lines.append(f"    Last Q: {last_qa.question[:50]}...")
                lines.append(f"    URL Check: {'✅' if last_qa.full_clip_url.startswith(self.base_url) else '❌'}")
        
        lines.append("="*70)
        return "\n".join(lines)

# Global debugger instance
_debugger: Optional[SessionDebugger] = None

def get_debugger() -> SessionDebugger:
    """Get or create debugger singleton"""
    global _debugger
    if _debugger is None:
        _debugger = SessionDebugger()
    return _debugger

def log_qa_session(**kwargs):
    """บันทึก QA session (convenience function)"""
    debugger = get_debugger()
    debugger.log_qa(**kwargs)

def print_session_summary():
    """แสดงสรุป sessions"""
    debugger = get_debugger()
    print(debugger.get_session_summary())

if __name__ == "__main__":
    # Test
    print_session_summary()
