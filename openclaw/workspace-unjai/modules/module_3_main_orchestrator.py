"""
Module 3: Main Orchestrator (The Brain of the Swarm)
Nong Unjai AI System

This module is the central coordinator that:
- Receives requests from LINE Gateway
- Orchestrates all other modules
- Makes decisions based on NLP analysis
- Routes to appropriate handlers
- Manages user state and persona transitions
- Handles crisis situations

Flow:
User Message → LINE Gateway → Orchestrator → [NLP/Search/Video/Middleware] → Response
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import httpx

from module_2_nlp_processor import NLPProcessor, NLPAnalysisResult
from module_4_line_gateway import LineGateway, FlexMessageBuilder, UserSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowStep(Enum):
    """Steps in the processing workflow"""
    RECEIVE = "receive"
    ANALYZE = "analyze"
    CHECK_CRISIS = "check_crisis"
    CHECK_INTENT = "check_intent"
    SEARCH_KNOWLEDGE = "search_knowledge"
    REQUEST_VIDEO = "request_video"
    HANDLE_QUIZ = "handle_quiz"
    UPDATE_COINS = "update_coins"
    BUILD_RESPONSE = "build_response"
    SEND_REPLY = "send_reply"


class IntentType(Enum):
    """Intent types from NLP"""
    GREETING = "greeting"
    SMALL_TALK = "small_talk"
    EMOTIONAL_SUPPORT = "emotional_support"
    BIBLE_QUESTION = "bible_question"
    THEOLOGY_QUESTION = "theology_question"
    CRISIS = "crisis"
    REQUEST_VIDEO = "request_video"
    QUIZ_ANSWER = "quiz_answer"
    GRATITUDE = "gratitude"
    COMPLAINT = "complaint"
    GOODBYE = "goodbye"
    UNKNOWN = "unknown"


@dataclass
class WorkflowContext:
    """Context passed through the workflow"""
    user_id: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # NLP Results
    sentiment_score: float = 0.0
    sentiment_label: str = ""
    primary_intent: Optional[IntentType] = None
    intent_confidence: float = 0.0
    emotions: List[str] = field(default_factory=list)
    crisis_level: str = "NONE"
    is_crisis: bool = False
    r_score: float = 50.0
    recommended_persona: int = 6
    recommended_circle: int = 1
    
    # Knowledge Results
    knowledge_results: List[Dict] = field(default_factory=list)
    scripture_found: bool = False
    
    # Video/Quiz Results
    video_url: Optional[str] = None
    quiz_id: Optional[str] = None
    quiz_result: Optional[Dict] = None
    
    # Response
    response_type: str = "text"
    response_content: str = ""
    response_data: Dict = field(default_factory=dict)
    
    # Metadata
    processing_time_ms: int = 0
    steps_executed: List[str] = field(default_factory=list)


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator"""
    # Middleware endpoints
    middleware_video_url: str = "http://middleware:8000/api/video"
    middleware_quiz_url: str = "http://middleware:8000/api/quiz"
    
    # Knowledge base settings
    knowledge_base_url: str = "http://localhost:8001"
    
    # MAAC settings (if needed)
    maac_api_url: str = "http://maac:8000/api"
    
    # R-score thresholds
    r_score_low_threshold: float = 40.0
    r_score_high_threshold: float = 80.0
    
    # Timeout settings
    video_request_timeout: int = 30
    knowledge_search_timeout: int = 5


class MainOrchestrator:
    """
    Main Orchestrator - Central controller for all modules
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        
        # Initialize modules
        self.nlp_processor = NLPProcessor()
        self.flex_builder = FlexMessageBuilder()
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Middleware callbacks (to be set)
        self.video_callback: Optional[Callable] = None
        self.quiz_callback: Optional[Callable] = None
        self.coin_callback: Optional[Callable] = None
        
        logger.info("Main Orchestrator initialized")
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        session: UserSession
    ) -> Dict[str, Any]:
        """
        Main entry point - process a user message through the full workflow
        """
        start_time = datetime.now()
        context = WorkflowContext(user_id=user_id, message=message)
        
        try:
            # Step 1: Analyze with NLP
            context = await self._step_analyze(context, session)
            
            # Step 2: Check for crisis
            context = await self._step_check_crisis(context, session)
            if context.is_crisis:
                return await self._build_crisis_response(context, session)
            
            # Step 3: Route based on intent
            context = await self._step_route_intent(context, session)
            
            # Step 4: Build final response
            response = await self._build_response(context, session)
            
            # Update session
            self._update_session(context, session)
            
            # Calculate processing time
            context.processing_time_ms = int(
                (datetime.now() - start_time).total_seconds() * 1000
            )
            
            logger.info(
                f"Processed message for {user_id}: "
                f"intent={context.primary_intent}, "
                f"persona={context.recommended_persona}, "
                f"time={context.processing_time_ms}ms"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._build_error_response()
    
    async def _step_analyze(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> WorkflowContext:
        """Step 1: Analyze message with NLP"""
        context.steps_executed.append(WorkflowStep.ANALYZE.value)
        
        # Run NLP analysis
        nlp_result = self.nlp_processor.analyze(context.message)
        
        # Extract results
        context.sentiment_score = nlp_result.sentiment.score
        context.sentiment_label = nlp_result.sentiment.label.name
        context.primary_intent = IntentType(nlp_result.intent.primary_intent.value)
        context.intent_confidence = nlp_result.intent.confidence
        context.emotions = nlp_result.sentiment.emotions
        context.crisis_level = nlp_result.crisis.level.name
        context.is_crisis = nlp_result.crisis.is_crisis
        context.r_score = nlp_result.r_score
        context.recommended_persona = nlp_result.recommended_persona
        context.recommended_circle = nlp_result.recommended_circle
        
        logger.debug(f"NLP Analysis: intent={context.primary_intent}, "
                    f"sentiment={context.sentiment_label}")
        
        return context
    
    async def _step_check_crisis(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> WorkflowContext:
        """Step 2: Check for crisis situation"""
        context.steps_executed.append(WorkflowStep.CHECK_CRISIS.value)
        
        if context.is_crisis:
            # Force Persona 8 (SOS)
            context.recommended_persona = 8
            logger.critical(f"CRISIS DETECTED for user {context.user_id}: "
                          f"level={context.crisis_level}")
        
        return context
    
    async def _step_route_intent(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> WorkflowContext:
        """Step 3: Route to appropriate handler based on intent"""
        context.steps_executed.append(WorkflowStep.CHECK_INTENT.value)
        
        intent_handlers = {
            IntentType.GREETING: self._handle_greeting,
            IntentType.SMALL_TALK: self._handle_small_talk,
            IntentType.EMOTIONAL_SUPPORT: self._handle_emotional_support,
            IntentType.BIBLE_QUESTION: self._handle_bible_question,
            IntentType.THEOLOGY_QUESTION: self._handle_bible_question,
            IntentType.CRISIS: self._handle_crisis,
            IntentType.REQUEST_VIDEO: self._handle_video_request,
            IntentType.QUIZ_ANSWER: self._handle_quiz_answer,
            IntentType.GRATITUDE: self._handle_gratitude,
            IntentType.COMPLAINT: self._handle_emotional_support,
            IntentType.GOODBYE: self._handle_goodbye,
            IntentType.UNKNOWN: self._handle_unknown,
        }
        
        handler = intent_handlers.get(
            context.primary_intent,
            self._handle_unknown
        )
        
        return await handler(context, session)
    
    # Intent Handlers
    
    async def _handle_greeting(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> WorkflowContext:
        """Handle greeting intent"""
        # Check if first time
        if session.message_count <= 1:
            context.response_type = "text"
            context.response_content = (
                "สวัสดีค่ะ! น้องอุ่นใจยินดีที่ได้รู้จักค่ะ 💙\n\n"
                "คุณพี่อยากคุยเรื่องอะไรดีคะ? "
                "ถ้าอยากดูคลิปหนุนใจ หรือถามเรื่องพระคัมภีร์ บอกอุ่นใจได้เลยนะคะ"
            )
        else:
            context.response_type = "text"
            context.response_content = (
                f"สวัสดีค่ะคุณพี่! วันนี้เป็นยังไงบ้างคะ? "
                f"อุ่นใจอยู่ตรงนี้เสมอนะคะ 💙"
            )
        
        return context
    
    async def _handle_small_talk(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> WorkflowContext:
        """Handle small talk"""
        context.response_type = "quick_reply"
        context.response_content = (
            "อุ่นใจสบายดีค่ะ! ขอบคุณที่ถามนะคะ 💙\n"
            "คุณพี่วันนี้เป็นยังไงบ้างคะ?"
        )
        context.response_data["options"] = [
            {"label": "😊 ดีค่ะ", "text": "วันนี้ดีค่ะ"},
            {"label": "😔 นอยๆ", "text": "วันนี้รู้สึกนอยๆ"},
            {"label": "🎥 ขอคลิป", "text": "ขอคลิปหนุนใจ"},
        ]
        return context
    
    async def _handle_emotional_support(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> WorkflowContext:
        """Handle emotional support request"""
        # Search for relevant content
        context = await self._search_knowledge(context, "emotional_support")
        
        # Recommend Persona 2 (Healing)
        context.recommended_persona = 2
        
        context.response_type = "flex"
        context.response_content = "ส่งกำลังใจให้คุณพี่ค่ะ 💙"
        
        # Build flex message with video if available
        if context.video_url:
            flex_content = self.flex_builder.create_video_card(
                title="ข้อความหนุนใจสำหรับคุณพี่",
                description="พระเจ้าทรงรักและดูแลคุณพี่เสมอค่ะ",
                video_url=context.video_url,
                thumbnail_url=context.video_url.replace(".mp4", "_thumb.jpg"),
                duration="05:00",
                scripture="ยอห์น 3:16",
                tags=["encouragement", "healing"]
            )
            context.response_data["flex_content"] = flex_content
            context.response_data["alt_text"] = "วิดีโอหนุนใจ"
        else:
            context.response_type = "text"
            context.response_content = (
                "อุ่นใจเข้าใจความรู้สึกของคุณพี่ค่ะ 💙\n\n"
                "พระคัมภีร์บอกว่า 'พระเจ้าทรงเป็นที่ลี้ภัยของเรา'\n"
                "คุณพี่ไม่ได้อยู่คนเดียวนะคะ อุ่นใจอยู่ตรงนี้เสมอค่ะ\n\n"
                "อยากให้อุ่นใจส่งคลิปหนุนใจให้ไหมคะ?"
            )
        
        return context
    
    async def _handle_bible_question(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> WorkflowContext:
        """Handle bible/theology questions"""
        context = await self._search_knowledge(context, "bible")
        
        # Recommend Persona 1 (Intellectual)
        context.recommended_persona = 1
        
        if context.knowledge_results:
            result = context.knowledge_results[0]
            context.response_type = "text"
            context.response_content = (
                f"คุณพี่ถามดีมากค่ะ! 💙\n\n"
                f"จากที่อุ่นใจค้นหา พบว่า:\n\n"
                f"{result.get('content', 'ขออภัย ไม่พบข้อมูลค่ะ')}\n\n"
                f"อยากให้อธิบายเพิ่มเติมตรงไหนไหมคะ?"
            )
        else:
            context.response_type = "text"
            context.response_content = (
                "คุณพี่ถามดีมากค่ะ! 💙\n\n"
                "อุ่นใจขออภัยที่ยังไม่มีคำตอบสำหรับคำถามนี้\n"
                "อยากให้อุ่นใจค้นหาข้อมูลเพิ่มเติมไหมคะ?"
            )
        
        return context
    
    async def _handle_crisis(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> WorkflowContext:
        """Handle crisis - delegate to crisis handler"""
        context.recommended_persona = 8  # SOS Persona
        return context
    
    async def _handle_video_request(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> WorkflowContext:
        """Handle video request"""
        context = await self._request_video_from_middleware(context)
        
        # Recommend Persona based on emotional state
        if context.sentiment_score < -0.3:
            context.recommended_persona = 2  # Healing
        else:
            context.recommended_persona = 3  # Social
        
        return context
    
    async def _handle_quiz_answer(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> WorkflowContext:
        """Handle quiz answer"""
        # Parse answer from message
        # This would integrate with quiz validation from middleware/MAAC
        
        context.response_type = "text"
        context.response_content = (
            "ขอบคุณสำหรับคำตอบค่ะ! 💙\n\n"
            "อุ่นใจจะตรวจคำตอบและแจ้งผลให้นะคะ\n"
            "ถ้าตอบถูกจะได้รับ Smart Coins ด้วยค่ะ!"
        )
        
        return context
    
    async def _handle_gratitude(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> WorkflowContext:
        """Handle gratitude"""
        context.response_type = "text"
        context.response_content = (
            "ด้วยความยินดีค่ะคุณพี่! 💙\n\n"
            "อุ่นใจดีใจที่ได้ช่วยเหลือค่ะ\n"
            "ถ้ามีอะไรอยากคุยอีก บอกอุ่นใจได้เสมอนะคะ"
        )
        return context
    
    async def _handle_goodbye(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> WorkflowContext:
        """Handle goodbye"""
        context.response_type = "text"
        context.response_content = (
            "ลาก่อนค่ะคุณพี่! 💙\n\n"
            "อุ่นใจจะอยู่ตรงนี้เสมอนะคะ\n"
            "ไว้มาคุยกันใหม่น้า~"
        )
        return context
    
    async def _handle_unknown(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> WorkflowContext:
        """Handle unknown intent"""
        context.response_type = "quick_reply"
        context.response_content = (
            "ขออภัยค่ะ อุ่นใจไม่แน่ใจว่าเข้าใจถูกไหม\n"
            "คุณพี่ต้องการอะไรคะ?"
        )
        context.response_data["options"] = [
            {"label": "🎥 ขอคลิป", "text": "ขอคลิปหนุนใจ"},
            {"label": "📖 ถามพระคัมภีร์", "text": "มีคำถามเรื่องพระคัมภีร์"},
            {"label": "💬 คุยเล่น", "text": "อยากคุยกับอุ่นใจ"},
        ]
        return context
    
    # Helper Methods
    
    async def _search_knowledge(
        self,
        context: WorkflowContext,
        query_type: str
    ) -> WorkflowContext:
        """Search knowledge base"""
        context.steps_executed.append(WorkflowStep.SEARCH_KNOWLEDGE.value)
        
        try:
            # This would call Module 1 (Knowledge Base)
            # For now, simulate results
            context.knowledge_results = [
                {
                    "content": "พระเจ้าทรงรักโลก...",
                    "source": "ยอห์น 3:16",
                    "circle": context.recommended_circle
                }
            ]
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
        
        return context
    
    async def _request_video_from_middleware(
        self,
        context: WorkflowContext
    ) -> WorkflowContext:
        """Request video from middleware"""
        context.steps_executed.append(WorkflowStep.REQUEST_VIDEO.value)
        
        try:
            # This would call the middleware
            # Simulate for now
            context.video_url = "https://example.com/video.mp4"
            
            if self.video_callback:
                video_result = await self.video_callback(context.message)
                context.video_url = video_result.get("url")
        except Exception as e:
            logger.error(f"Error requesting video: {e}")
        
        return context
    
    async def _build_crisis_response(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> Dict[str, Any]:
        """Build crisis response (Persona 8)"""
        return {
            "type": "text",
            "content": (
                "คุณพี่คะ! หยุดก่อนนะคะ! อุ่นใจอยู่นี่ค่ะ 💙\n\n"
                "อุ่นใจกำลังติดต่อพี่อาสามาช่วยเหลือคุณพี่นะคะ\n"
                "คุณพี่ไม่ได้อยู่คนเดียวค่ะ...\n\n"
                "☎️ สายด่วนสุขภาพจิต: 1323\n"
                "☎️ หน่วยกู้ชีพ: 1669"
            ),
            "crisis_alert": True,
            "persona": 8
        }
    
    async def _build_response(
        self,
        context: WorkflowContext,
        session: UserSession
    ) -> Dict[str, Any]:
        """Build final response"""
        context.steps_executed.append(WorkflowStep.BUILD_RESPONSE.value)
        
        # Add persona signature based on recommended persona
        persona_signatures = {
            1: "\n\n— พี่สาวสายปัญญา 💙",      # Intellectual
            2: "\n\n— เพื่อนสาวสายเยียวยา 💙",   # Healing
            3: "\n\n— น้องสาวสายกิจกรรม 💙",     # Social
            6: "\n\n— น้องอุ่นใจ 💙",             # Watcher (default)
            8: "\n\n— หน่วยกู้ใจสายด่วน 💙",     # SOS
        }
        
        if context.response_type == "text":
            signature = persona_signatures.get(context.recommended_persona, "")
            context.response_content += signature
        
        response = {
            "type": context.response_type,
            "content": context.response_content,
            "persona": context.recommended_persona,
            "circle": context.recommended_circle,
            "r_score": context.r_score,
            "intent": context.primary_intent.value if context.primary_intent else "unknown"
        }
        
        # Add flex content if present
        if context.response_data.get("flex_content"):
            response["flex_content"] = context.response_data["flex_content"]
            response["alt_text"] = context.response_data.get("alt_text", "Message")
        
        # Add quick reply options if present
        if context.response_data.get("options"):
            response["options"] = context.response_data["options"]
        
        return response
    
    def _update_session(self, context: WorkflowContext, session: UserSession):
        """Update user session with results"""
        # Update persona and circle based on recommendation
        session.current_persona = context.recommended_persona
        session.current_circle = context.recommended_circle
        session.r_score = context.r_score
        
        # Set crisis flag if applicable
        if context.is_crisis:
            session.crisis_flag = True
        
        # Add assistant message to history
        session.add_message("assistant", context.response_content)
    
    def _build_error_response(self) -> Dict[str, Any]:
        """Build error response"""
        return {
            "type": "text",
            "content": (
                "ขออภัยค่ะ ระบบมีปัญหาเล็กน้อย\n"
                "กรุณาลองใหม่อีกครั้งนะคะ 💙"
            ),
            "persona": 6,
            "error": True
        }
    
    # Callback setters
    
    def set_video_callback(self, callback: Callable):
        """Set callback for video requests"""
        self.video_callback = callback
    
    def set_quiz_callback(self, callback: Callable):
        """Set callback for quiz validation"""
        self.quiz_callback = callback
    
    def set_coin_callback(self, callback: Callable):
        """Set callback for coin operations"""
        self.coin_callback = callback
    
    def get_health(self) -> Dict[str, Any]:
        """Get orchestrator health status"""
        return {
            "status": "healthy",
            "components": {
                "nlp_processor": "active",
                "flex_builder": "active",
                "http_client": "active"
            },
            "timestamp": datetime.now().isoformat()
        }


# Integration with LINE Gateway
class OrchestratedLineGateway:
    """
    Integration class that connects LineGateway with MainOrchestrator
    """
    
    def __init__(self):
        self.line_gateway = LineGateway()
        self.orchestrator = MainOrchestrator()
        
        # Set up handlers
        self.line_gateway.set_message_handler(self._handle_message)
        self.line_gateway.set_crisis_handler(self._handle_crisis)
    
    async def _handle_message(
        self,
        parsed_message,
        session: UserSession
    ) -> Dict[str, Any]:
        """Handle normal messages"""
        return await self.orchestrator.process_message(
            user_id=parsed_message.user_id,
            message=parsed_message.content,
            session=session
        )
    
    async def _handle_crisis(
        self,
        parsed_message,
        session: UserSession
    ) -> Dict[str, Any]:
        """Handle crisis detection"""
        # Run through orchestrator which will detect crisis
        result = await self.orchestrator.process_message(
            user_id=parsed_message.user_id,
            message=parsed_message.content,
            session=session
        )
        
        return {
            "is_crisis": result.get("persona") == 8,
            "level": "EMERGENCY" if result.get("persona") == 8 else "NONE"
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_orchestrator():
        print("=" * 70)
        print("🎛️ Main Orchestrator Test")
        print("=" * 70)
        
        orchestrator = MainOrchestrator()
        
        test_messages = [
            ("สวัสดีค่ะ", "Greeting"),
            ("วันนี้รู้สึกนอยๆ", "Emotional support"),
            ("ยอห์น 3:16 ว่าอะไร", "Bible question"),
            ("ขอคลิปหนุนใจ", "Video request"),
            ("อยากตาย ไม่อยากอยู่แล้ว", "Crisis"),
        ]
        
        for msg, desc in test_messages:
            print(f"\n📝 Test: {desc}")
            print(f"   Input: '{msg}'")
            
            # Mock session
            from module_4_line_gateway import UserSession
            session = UserSession(user_id="test_user")
            session.add_message("user", msg)
            
            result = await orchestrator.process_message(
                user_id="test_user",
                message=msg,
                session=session
            )
            
            print(f"   Type: {result['type']}")
            print(f"   Persona: {result['persona']}")
            print(f"   Intent: {result.get('intent', 'unknown')}")
            print(f"   Response: {result['content'][:50]}...")
        
        print("\n" + "=" * 70)
        print("✅ Test completed!")
        print("=" * 70)
    
    asyncio.run(test_orchestrator())
