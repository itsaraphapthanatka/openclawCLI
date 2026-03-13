"""
Search Specialist Integration for Agent
Enables automatic video search in conversations
"""
from typing import Dict, List, Optional
import json

class SearchSpecialistIntegration:
    """
    Integration layer that allows the Agent (อุ่นใจ) to use Search Specialist automatically
    """
    
    def __init__(self):
        self.search_specialist = None
        self._load_search_specialist()
    
    def _load_search_specialist(self):
        """Lazy load Search Specialist"""
        try:
            from modules.pinecone_tool import get_search_specialist
            self.search_specialist = get_search_specialist()
            print("✅ Search Specialist loaded successfully")
        except Exception as e:
            print(f"⚠️ Search Specialist not available: {e}")
            self.search_specialist = None
    
    def search_videos(self, query: str, min_score: float = 0.70, 
                     top_k: int = 3) -> List[Dict]:
        """
        ค้นหาวิดีโออัตโนมัติจาก Pinecone
        
        Args:
            query: คำค้นหา (เช่น "การให้อภัย", "บาป")
            min_score: คะแนนขั้นต่ำ (0.70 = 70% match)
            top_k: จำนวนผลลัพธ์สูงสุด
        
        Returns:
            List ของวิดีโอที่ตรงกับคำค้นหา
        """
        if not self.search_specialist:
            print("❌ Search Specialist not available")
            return []
        
        result = self.search_specialist.search(query, top_k=top_k, 
                                               min_score=min_score)
        return result.get("video_results", [])
    
    def get_video_by_id(self, clip_id: str) -> Optional[Dict]:
        """ดึงข้อมูลวิดีโอจาก ID"""
        if not self.search_specialist:
            return None
        return self.search_specialist.search_by_id(clip_id)
    
    def should_send_video(self, query: str, r_score: int = 0) -> bool:
        """
        Journey Architect: ตัดสินใจว่าควรส่งวิดีโอหรือไม่
        (3-Filter System จาก AGENTS.md)
        """
        # Filter 1: Intent-based keywords
        video_keywords = ["วิดีโอ", "คลิป", "ดู", "ฟัง", "เรียนรู้"]
        emotional_keywords = ["เศร้า", "ท้อ", "เหนื่อย", "นอยด์"]
        
        has_video_intent = any(kw in query for kw in video_keywords)
        is_emotional = any(kw in query for kw in emotional_keywords)
        
        # Filter 2: R-Score threshold
        if r_score < 30 and not has_video_intent:
            return False  # ยังไม่ไว้ใจพอ ส่ง text ก่อน
        
        # Filter 3: Check if video exists
        videos = self.search_videos(query, min_score=0.75, top_k=1)
        if not videos:
            return False  # ไม่มีวิดีโอตรงกับคำถาม
        
        return True
    
    def format_flex_message(self, video: Dict) -> Dict:
        """
        แปลงข้อมูลวิดีโอเป็น Flex Message JSON
        """
        metadata = video.get("metadata", {})
        clip_url = metadata.get("clip_url", "")
        transcript = metadata.get("transcript", "")[:100] + "..."
        quiz = metadata.get("quiz", "[]")
        
        # Parse quiz if exists
        has_quiz = quiz != "[]"
        
        flex_content = {
            "type": "bubble",
            "hero": {
                "type": "video",
                "url": clip_url,
                "previewUrl": f"https://i.ytimg.com/vi/{metadata.get('video_id', '')}/maxresdefault.jpg",
                "altContent": {
                    "type": "image",
                    "url": f"https://i.ytimg.com/vi/{metadata.get('video_id', '')}/maxresdefault.jpg",
                    "size": "full",
                    "aspectRatio": "16:9",
                    "aspectMode": "cover"
                },
                "aspectRatio": "16:9"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": f"🎬 คลิปหนุนใจ (Score: {video.get('score', 0):.2f})",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#FF84AA"
                    },
                    {
                        "type": "text",
                        "text": transcript,
                        "size": "sm",
                        "wrap": True,
                        "color": "#666666"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#FF84AA",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "🎯 ทำควิซรับเหรียญ" if has_quiz else "👍 ขอบคุณค่ะ",
                            "text": "ทำควิซ" if has_quiz else "ขอบคุณ"
                        }
                    }
                ]
            }
        }
        
        return {
            "type": "flex",
            "altText": "คลิปหนุนใจจากอุ่นใจ",
            "contents": flex_content
        }
    
    def process_user_query(self, user_message: str, r_score: int = 0) -> Optional[Dict]:
        """
        ประมวลผลคำถามผู้ใช้อัตโนมัติ
        
        Returns:
            Flex Message ถ้าควรส่งวิดีโอ
            None ถ้าควรตอบด้วย text ธรรมดา
        """
        # Check if should send video
        if not self.should_send_video(user_message, r_score):
            return None
        
        # Search videos
        videos = self.search_videos(user_message, min_score=0.70, top_k=1)
        
        if not videos:
            return None
        
        # Return Flex Message for best match
        best_video = videos[0]
        return self.format_flex_message(best_video)


# Global instance
_search_integration = None

def get_search_integration():
    """Get Search Specialist integration"""
    global _search_integration
    if _search_integration is None:
        _search_integration = SearchSpecialistIntegration()
    return _search_integration


# Example integration in Agent response
async def agent_response_with_video(user_message: str, r_score: int = 0):
    """
    Example: How Agent uses Search Specialist automatically
    """
    integration = get_search_integration()
    
    # Try to find video
    flex_message = integration.process_user_query(user_message, r_score)
    
    if flex_message:
        # Send video
        return {
            "type": "video_found",
            "flex_message": flex_message,
            "message": "อุ่นใจเจอคลิปที่ตรงกับคำถามคุณพี่ค่ะ! 💕"
        }
    else:
        # Send text only
        return {
            "type": "text_only",
            "message": "อุ่นใจขอตอบด้วยข้อความนะคะ..."
        }
