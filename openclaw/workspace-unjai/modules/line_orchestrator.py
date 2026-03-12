"""
LINE Gateway + Search Specialist Integration
Nong Unjai AI System - Production Ready

This module connects LINE Gateway with Pinecone Search
for real-time video content retrieval.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Import from modules
from modules.module_4_line_gateway import (
    LineGateway, ParsedMessage, UserSession, 
    FlexMessageBuilder, MessageType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchSpecialistConnector:
    """
    Agent: Search Specialist (Enhanced for LINE)
    
    Task: ค้นหาข้อมูลแบบ Parallel ทั้งจาก MEMORY.md และ Pinecone
          และส่งตัวเลือกให้ Journey Architect ตัดสินใจ
    """
    
    def __init__(self):
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_index = os.getenv("PINECONE_INDEX_NAME", "aunjai-knowledge")
        self.namespace = os.getenv("PINECONE_NAMESPACE", "highlights")
        self.index_host = os.getenv("PINECONE_INDEX_HOST")
        
        # Embedding model (ใช้ OpenAI หรือ HuggingFace)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        logger.info("🔍 Search Specialist Connector initialized")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """สร้าง embedding vector จากข้อความ"""
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000]  # Limit text length
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            # Return zero vector as fallback (384 dimensions for Pinecone)
            return [0.0] * 384
    
    async def search_pinecone(self, 
                             query_embedding: List[float],
                             top_k: int = 3,
                             min_score: float = 0.70) -> List[Dict]:
        """
        ค้นหา video highlights ใน Pinecone
        
        Returns:
            List of video results with clip_url, transcript, score
        """
        try:
            import httpx
            
            url = f"{self.index_host}/query"
            headers = {
                "Api-Key": self.pinecone_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "namespace": self.namespace,
                "vector": query_embedding,
                "topK": top_k,
                "includeMetadata": True,
                "includeValues": False
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                matches = data.get("matches", [])
                
                # Filter results with minimum score and clip_url
                filtered = []
                for match in matches:
                    score = match.get("score", 0)
                    metadata = match.get("metadata", {})
                    
                    if score >= min_score and metadata.get("clip_url"):
                        filtered.append({
                            "id": match["id"],
                            "score": score,
                            "clip_url": metadata.get("clip_url"),
                            "video_url": metadata.get("video_url"),
                            "start_time": metadata.get("start_time"),
                            "end_time": metadata.get("end_time"),
                            "transcript": metadata.get("transcript", ""),
                            "reason": metadata.get("reason", ""),
                            "type": metadata.get("type", "highlight")
                        })
                
                logger.info(f"✅ Found {len(filtered)} videos in Pinecone (min_score={min_score})")
                return filtered
                
        except Exception as e:
            logger.error(f"❌ Error searching Pinecone: {e}")
            return []
    
    async def search_memory_md(self, query: str) -> List[Dict]:
        """
        ค้นหาใน MEMORY.md (จะถูกเรียกผ่าน memory_search tool)
        
        Note: ใน production ควรใช้ memory_search tool โดยตรง
        """
        # Placeholder - ในระบบจริงจะเรียกผ่าน memory_search
        return []
    
    async def parallel_search(self, 
                             user_message: str,
                             top_k: int = 3) -> Dict[str, Any]:
        """
        🔍 Parallel Hybrid Search
        
        ค้นหาพร้อมกันทั้งจาก Pinecone (video) และเตรียมข้อมูลสำหรับ MEMORY.md
        
        Returns:
            {
                "query_embedding": [...],
                "video_results": [...],
                "text_results": [...],
                "has_highlights": bool
            }
        """
        logger.info(f"🔍 Search Specialist: Searching for \"{user_message[:50]}...\"")
        
        # 1. สร้าง embedding จากข้อความผู้ใช้
        embedding = await self.generate_embedding(user_message)
        
        # 2. ค้นหาใน Pinecone (video highlights)
        video_results = await self.search_pinecone(
            embedding, 
            top_k=top_k,
            min_score=0.70
        )
        
        # 3. ส่งผลลัพธ์รวม
        results = {
            "query_embedding": embedding,
            "video_results": video_results,
            "text_results": [],  # จะถูกเติมโดย memory_search
            "has_highlights": len(video_results) > 0
        }
        
        logger.info(f"✅ Parallel search complete: {len(video_results)} videos found")
        return results


class JourneyArchitectDecision:
    """
    Agent: Journey Architect
    
    Task: ใช้ 3-Filter System ตัดสินใจว่าจะส่งอะไรกลับไป
    """
    
    def __init__(self):
        self.flex_builder = FlexMessageBuilder()
    
    def decide_response_type(self,
                            user_message: str,
                            session: UserSession,
                            search_results: Dict) -> str:
        """
        🎯 3-Filter System
        
        Returns: "text_only" | "video_nudge" | "video_package"
        """
        r_score = session.r_score
        video_results = search_results.get("video_results", [])
        has_highlights = len(video_results) > 0
        
        # Filter 1: Content Depth
        is_fact_check = any(word in user_message for word in [
            "ข้อ", "บท", "อ้างอิง", "กี่", "เท่าไหร่", "คืออะไร"
        ])
        
        is_emotional = any(word in user_message for word in [
            "เศร้า", "เหนื่อย", "ท้อ", "กังวล", "เครียด", "เจ็บปวด"
        ])
        
        # Filter 2: R-Score Threshold
        if r_score < 30:
            # ผู้ใช้ใหม่ - สร้างความไว้วางใจก่อน
            return "text_only"
        
        elif 30 <= r_score < 60:
            # ผู้ใช้เริ่มสนิท - แนะนำวิดีโอเบาๆ
            if has_highlights and is_emotional:
                return "video_nudge"
            return "text_only"
        
        else:  # r_score >= 60
            # ผู้ใช้วงใน - ส่งวิดีโอเต็มรูปแบบ
            
            # Filter 3: Interest Match
            if has_highlights:
                if is_emotional or is_fact_check:
                    return "video_package"
            
            return "text_only"
    
    def build_response(self,
                      decision: str,
                      user_message: str,
                      session: UserSession,
                      search_results: Dict,
                      text_content: str) -> Dict:
        """
        สร้าง response ตามการตัดสินใจ
        """
        video_results = search_results.get("video_results", [])
        
        if decision == "text_only":
            return {
                "type": "text",
                "content": text_content
            }
        
        elif decision == "video_nudge":
            # แนะนำวิดีโอเบาๆ พร้อมข้อความ
            if video_results:
                video = video_results[0]
                flex_content = self.flex_builder.create_video_card(
                    title="🎬 คลิปหนุนใจ",
                    description=video.get("transcript", "")[:100],
                    video_url=video.get("clip_url", ""),
                    thumbnail_url=f"https://img.youtube.com/vi/{self._extract_video_id(video.get('video_url', ''))}/0.jpg",
                    scripture="",
                    tags=["หนุนใจ"]
                )
                
                return {
                    "type": "flex",
                    "flex_content": flex_content,
                    "alt_text": "🎬 คลิปหนุนใจจากน้องอุ่นใจ"
                }
            
            return {
                "type": "text",
                "content": text_content
            }
        
        elif decision == "video_package":
            # ส่งวิดีโอ + Quiz (สำหรับ Circle 2+)
            if video_results:
                video = video_results[0]
                
                # Build carousel with video and quiz preview
                bubbles = []
                
                # Video bubble
                video_bubble = self.flex_builder.create_video_card(
                    title="🎬 ดูวิดีโอนี้สิคะ",
                    description=video.get("reason", video.get("transcript", ""))[:100],
                    video_url=video.get("clip_url", ""),
                    thumbnail_url=f"https://img.youtube.com/vi/{self._extract_video_id(video.get('video_url', ''))}/0.jpg",
                    scripture="",
                    tags=["แนะนำ"]
                )
                bubbles.append(video_bubble)
                
                # Quiz bubble (placeholder)
                quiz_bubble = self.flex_builder.create_quiz_card(
                    question="พร้อมทำควิซหลังดูวิดีโอไหมคะ?",
                    choices=["พร้อมเลย!", "ขอดูก่อน"],
                    quiz_id="intro_quiz"
                )
                bubbles.append(quiz_bubble)
                
                return {
                    "type": "flex",
                    "flex_content": self.flex_builder.create_carousel(bubbles),
                    "alt_text": "🎬 วิดีโอ + 🎯 ควิซจากน้องอุ่นใจ"
                }
            
            return {
                "type": "text",
                "content": text_content
            }
        
        return {
            "type": "text",
            "content": text_content
        }
    
    def _extract_video_id(self, youtube_url: str) -> str:
        """Extract YouTube video ID from URL"""
        if "v=" in youtube_url:
            return youtube_url.split("v=")[1].split("&")[0]
        elif "/" in youtube_url:
            return youtube_url.split("/")[-1]
        return ""


class LineOrchestrator:
    """
    Main Orchestrator - เชื่อมทุกส่วนเข้าด้วยกัน
    
    Flow: LINE Gateway → Search Specialist → Journey Architect → Response
    """
    
    def __init__(self):
        self.line_gateway = LineGateway()
        self.search_specialist = SearchSpecialistConnector()
        self.journey_architect = JourneyArchitectDecision()
        
        # Set up message handler
        self.line_gateway.message_handler = self.handle_message
        
        logger.info("🤖 LineOrchestrator initialized and ready")
    
    async def handle_message(self, 
                            parsed: ParsedMessage, 
                            session: UserSession) -> Dict:
        """
        จัดการข้อความจากผู้ใช้ - Main Entry Point
        """
        user_message = parsed.content
        user_id = parsed.user_id
        
        logger.info(f"📩 Message from {user_id}: {user_message[:50]}...")
        
        # 1. 🔍 Search Specialist - Parallel Search
        search_results = await self.search_specialist.parallel_search(user_message)
        
        # 2. 🎯 Journey Architect - 3-Filter Decision
        decision = self.journey_architect.decide_response_type(
            user_message, session, search_results
        )
        
        logger.info(f"🎯 Decision: {decision} (R-score: {session.r_score})")
        
        # 3. 📝 Generate text content (from MEMORY.md หรือ AI)
        # Note: ในระบบจริงจะเรียก memory_search ที่นี่
        text_content = await self._generate_text_response(
            user_message, session, search_results
        )
        
        # 4. 📤 Build final response
        response = self.journey_architect.build_response(
            decision, user_message, session, search_results, text_content
        )
        
        # 5. 📊 Update session
        if decision == "video_package":
            session.r_score += 5  # ดูวิดีโอ +5 points
        
        return response
    
    async def _generate_text_response(self,
                                     user_message: str,
                                     session: UserSession,
                                     search_results: Dict) -> str:
        """
        สร้างข้อความตอบกลับ (จาก MEMORY.md หรือ AI)
        
        Note: ในระบบจริงจะเรียก memory_search ที่นี่
        """
        # Placeholder - ใน production จะค้นหาใน MEMORY.md จริงๆ
        
        # ตัวอย่าง response ตาม Persona
        persona_responses = {
            1: f"คุณพี่คะ สำหรับคำถามนี้ อุ่นใจขอแบ่งปันความรู้จากพระคัมภีร์นะคะ 🙏",
            2: f"คุณพี่ขา... อุ่นใจเข้าใจความรู้สึกนี้นะคะ 💕",
            3: f"คุณพี่! มีอะไรน่าสนใจมาบอกค่ะ 🌟",
            4: f"สวัสดีค่ะคุณพี่ อุ่นใจขอสรุปเป็นข้อๆ แบบนี้นะคะ 📋",
            5: f"คุณพี่ขา อุ่นใจขออธิษฐานเผื่อนะคะ 🙏",
            6: f"สวัสดีค่ะคุณพี่ อุ่นใจคิดถึงคุณพี่นะคะ 🌸",
            7: f"น่าสนใจค่ะคุณพี่! ลองคิดดูแบบนี้ไหมคะ? 🤔",
            8: f"คุณพี่คะ! อุ่นใจอยู่ตรงนี้ค่ะ 🛑",
            9: f"สับมากค่ะคุณพี่! 🔥",
            10: f"เหนื่อยไหมคะคุณพี่? มาพักสักครู่ 🌿",
            11: f"เย่! คุณพี่! มาเล่นเกมกับอุ่นใจไหมคะ? 🎮",
            12: f"ยินดีต้อนรับค่ะคุณพี่! 🎉"
        }
        
        return persona_responses.get(
            session.current_persona, 
            "สวัสดีค่ะคุณพี่ อุ่นใจยินดีช่วยเหลือค่ะ 💕"
        )


# 🚀 Initialize and Export
line_orchestrator = LineOrchestrator()

# Export for use in main app
__all__ = [
    'line_orchestrator',
    'SearchSpecialistConnector',
    'JourneyArchitectDecision',
    'LineOrchestrator'
]
