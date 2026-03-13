"""
Module 4: LINE Gateway (The Digital Receptionist)
Nong Unjai AI System

This module handles:
- LINE Messaging API Webhook handling
- Message parsing (text, image, sticker, etc.)
- Flex Message builder for rich UI
- User session management
- Reply and Push message sending
- Integration with NLP Processor and Knowledge Base

Tech Stack:
- FastAPI (Webhook server)
- LINE SDK Python
- Redis (Session storage)
- WebSocket (Real-time communication)
"""

import os
import json
import hmac
import hashlib
import base64
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, HTTPException, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, StickerMessage,
    TextSendMessage, FlexSendMessage, QuickReply, QuickReplyButton,
    MessageAction, URIAction, PostbackAction, TemplateSendMessage,
    ButtonsTemplate, CarouselTemplate, CarouselColumn,
    ImageSendMessage, VideoSendMessage
)
import redis
import httpx
from pydantic import BaseModel

# Import Flex Message Templates
try:
    from flex_templates import FlexMessageBuilder
except ImportError:
    # Fallback if not available
    FlexMessageBuilder = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """LINE message types"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    LOCATION = "location"
    STICKER = "sticker"
    FLEX = "flex"


class UserAction(Enum):
    """User interaction types"""
    MESSAGE = "message"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    JOIN = "join"
    LEAVE = "leave"
    POSTBACK = "postback"
    BEACON = "beacon"


@dataclass
class LineUserProfile:
    """LINE user profile"""
    user_id: str
    display_name: str
    picture_url: Optional[str] = None
    status_message: Optional[str] = None
    language: str = "th"


@dataclass
class ParsedMessage:
    """Parsed LINE message"""
    message_id: str
    user_id: str
    message_type: MessageType
    content: str
    timestamp: datetime
    reply_token: Optional[str] = None
    raw_data: Optional[Dict] = None


@dataclass
class UserSession:
    """User session data"""
    user_id: str
    current_persona: int = 6  # Default: Passive Watcher
    current_circle: int = 1   # Default: Circle 1 (Self)
    r_score: float = 50.0
    conversation_history: List[Dict] = None
    last_interaction: datetime = None
    message_count: int = 0
    crisis_flag: bool = False
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.last_interaction is None:
            self.last_interaction = datetime.now()
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last 10 messages
        self.conversation_history = self.conversation_history[-10:]
        self.message_count += 1
        self.last_interaction = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "current_persona": self.current_persona,
            "current_circle": self.current_circle,
            "r_score": self.r_score,
            "conversation_history": self.conversation_history,
            "last_interaction": self.last_interaction.isoformat(),
            "message_count": self.message_count,
            "crisis_flag": self.crisis_flag
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "UserSession":
        session = cls(
            user_id=data["user_id"],
            current_persona=data.get("current_persona", 6),
            current_circle=data.get("current_circle", 1),
            r_score=data.get("r_score", 50.0),
            crisis_flag=data.get("crisis_flag", False)
        )
        session.conversation_history = data.get("conversation_history", [])
        session.message_count = data.get("message_count", 0)
        if "last_interaction" in data:
            session.last_interaction = datetime.fromisoformat(data["last_interaction"])
        return session


class SessionManager:
    """
    Manage user sessions with Redis
    """
    
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 6379, 
                 db: int = 1,
                 ttl: int = 86400):  # 24 hours
        self.redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self.ttl = ttl
        logger.info("SessionManager initialized")
    
    def get_session(self, user_id: str) -> UserSession:
        """Get or create user session"""
        key = f"session:{user_id}"
        data = self.redis.get(key)
        
        if data:
            try:
                session_data = json.loads(data)
                return UserSession.from_dict(session_data)
            except Exception as e:
                logger.error(f"Error parsing session: {e}")
        
        # Create new session
        return UserSession(user_id=user_id)
    
    def save_session(self, session: UserSession):
        """Save user session to Redis"""
        key = f"session:{session.user_id}"
        data = json.dumps(session.to_dict())
        self.redis.setex(key, self.ttl, data)
    
    def update_session(self, user_id: str, **kwargs):
        """Update specific fields in session"""
        session = self.get_session(user_id)
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        self.save_session(session)
    
    def clear_session(self, user_id: str):
        """Clear user session"""
        key = f"session:{user_id}"
        self.redis.delete(key)
    
    def get_active_users(self, minutes: int = 30) -> List[str]:
        """Get list of active users in last N minutes"""
        # This would require scanning or a separate index
        # Simplified version
        return []


class FlexMessageBuilder:
    """
    Build LINE Flex Messages for rich UI
    """
    
    @staticmethod
    def create_video_card(title: str, 
                          description: str,
                          video_url: str,
                          thumbnail_url: str,
                          duration: str = "",
                          scripture: str = "",
                          tags: List[str] = None) -> Dict:
        """Create a video card Flex Message"""
        
        tags = tags or []
        tag_bubbles = []
        for tag in tags[:3]:
            tag_bubbles.append({
                "type": "text",
                "text": f"#{tag}",
                "size": "xs",
                "color": "#888888",
                "margin": "sm"
            })
        
        flex_content = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": thumbnail_url,
                "size": "full",
                "aspectRatio": "16:9",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "uri": video_url
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "weight": "bold",
                        "size": "md",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": description[:100] + "..." if len(description) > 100 else description,
                        "size": "sm",
                        "color": "#666666",
                        "wrap": True,
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": tag_bubbles,
                        "margin": "md"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "▶ ดูวิดีโอ",
                            "uri": video_url
                        },
                        "style": "primary",
                        "color": "#FF6B6B"
                    }
                ]
            }
        }
        
        if scripture:
            flex_content["body"]["contents"].insert(1, {
                "type": "text",
                "text": f"📖 {scripture}",
                "size": "xs",
                "color": "#4A90E2",
                "margin": "sm"
            })
        
        if duration:
            flex_content["hero"]["contents"] = [{
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": duration,
                    "color": "#ffffff",
                    "size": "sm"
                }],
                "position": "absolute",
                "backgroundColor": "#00000088",
                "offsetEnd": "10px",
                "offsetBottom": "10px",
                "paddingAll": "5px",
                "cornerRadius": "5px"
            }]
        
        return flex_content
    
    @staticmethod
    def create_quiz_card(question: str, 
                         choices: List[str],
                         quiz_id: str) -> Dict:
        """Create a quiz card Flex Message"""
        
        choice_buttons = []
        for i, choice in enumerate(choices):
            choice_buttons.append({
                "type": "button",
                "action": {
                    "type": "postback",
                    "label": f"{chr(65+i)}. {choice[:20]}",
                    "data": f"quiz_answer|{quiz_id}|{chr(65+i)}"
                },
                "style": "secondary",
                "margin": "sm"
            })
        
        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🎯 ควิซหนุนใจ",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "lg"
                    }
                ],
                "backgroundColor": "#4A90E2"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": question,
                        "weight": "bold",
                        "size": "md",
                        "wrap": True
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": choice_buttons
            }
        }
    
    @staticmethod
    def create_progress_card(coins: int, 
                            r_score: float,
                            circle_level: int,
                            streak_days: int = 0) -> Dict:
        """Create user progress card"""
        
        circle_names = {1: "🌱 Self", 2: "❤️ Close Ones", 3: "🌍 Society"}
        circle_name = circle_names.get(circle_level, "🌱 Self")
        
        # Calculate progress bar
        progress = min(int(r_score), 100)
        progress_bar = "█" * (progress // 10) + "░" * (10 - progress // 10)
        
        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📊 สถิติของคุณ",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "lg"
                    }
                ],
                "backgroundColor": "#FF6B6B"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "🪙 Smart Coins:", "flex": 2},
                            {"type": "text", "text": str(coins), "flex": 1, "weight": "bold"}
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "💚 R-Score:", "flex": 2},
                            {"type": "text", "text": f"{r_score:.1f}", "flex": 1, "weight": "bold"}
                        ],
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": f"[{progress_bar}] {progress}%",
                        "size": "xs",
                        "color": "#888888",
                        "margin": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "🎯 Circle Level:", "flex": 2},
                            {"type": "text", "text": circle_name, "flex": 1, "weight": "bold"}
                        ],
                        "margin": "md"
                    }
                ]
            }
        }
    
    @staticmethod
    def create_carousel(bubbles: List[Dict]) -> Dict:
        """Create carousel from multiple bubbles"""
        return {
            "type": "carousel",
            "contents": bubbles
        }
    
    @staticmethod
    def create_quick_reply_buttons(options: List[Dict]) -> QuickReply:
        """Create quick reply buttons"""
        items = []
        for opt in options:
            items.append(
                QuickReplyButton(
                    action=MessageAction(
                        label=opt["label"],
                        text=opt["text"]
                    )
                )
            )
        return QuickReply(items=items)


class LineGateway:
    """
    Main LINE Gateway - handles webhooks and messaging
    """
    
    def __init__(self):
        # LINE API credentials
        self.channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self.channel_secret = os.getenv("LINE_CHANNEL_SECRET")
        
        # Base URL for clips and assets
        self.base_url = os.getenv("BASE_URL", "https://nongaunjai.febradio.org")
        logger.info(f"LINE Gateway Base URL: {self.base_url}")
        
        # Initialize LINE API
        self.line_bot_api = LineBotApi(self.channel_access_token)
        self.handler = WebhookHandler(self.channel_secret)
        
        # Initialize session manager
        self.session_manager = SessionManager(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379))
        )
        
        # Initialize flex builder
        self.flex_builder = FlexMessageBuilder()
        
        # Message handler callbacks (to be set by main app)
        self.message_handler: Optional[Callable] = None
        self.crisis_handler: Optional[Callable] = None
        
        logger.info("LINE Gateway initialized")
    
    def _ensure_full_url(self, url: str) -> str:
        """Ensure URL has base URL prefix"""
        if not url:
            return url
        if url.startswith("http://") or url.startswith("https://"):
            return url
        # Add base URL prefix
        return f"{self.base_url}{url}"
    
    def verify_signature(self, body: str, signature: str) -> bool:
        """Verify LINE webhook signature"""
        try:
            hash = hmac.new(
                self.channel_secret.encode('utf-8'),
                body.encode('utf-8'),
                hashlib.sha256
            ).digest()
            expected_signature = base64.b64encode(hash).decode('utf-8')
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    def parse_event(self, event: Dict) -> Optional[ParsedMessage]:
        """Parse LINE event into ParsedMessage"""
        try:
            event_type = event.get("type")
            
            if event_type == "message":
                message = event.get("message", {})
                message_type = message.get("type")
                
                content = ""
                if message_type == "text":
                    content = message.get("text", "")
                elif message_type == "sticker":
                    content = f"[Sticker:{message.get('stickerId')}"
                elif message_type == "image":
                    content = "[Image]"
                else:
                    content = f"[{message_type}]"
                
                return ParsedMessage(
                    message_id=message.get("id"),
                    user_id=event.get("source", {}).get("userId"),
                    message_type=MessageType(message_type) if message_type in [t.value for t in MessageType] else MessageType.TEXT,
                    content=content,
                    timestamp=datetime.fromtimestamp(event.get("timestamp", 0) / 1000),
                    reply_token=event.get("replyToken"),
                    raw_data=event
                )
            
            elif event_type == "follow":
                # User added the bot
                return ParsedMessage(
                    message_id="follow",
                    user_id=event.get("source", {}).get("userId"),
                    message_type=MessageType.TEXT,
                    content="[FOLLOW_EVENT]",
                    timestamp=datetime.fromtimestamp(event.get("timestamp", 0) / 1000),
                    reply_token=event.get("replyToken"),
                    raw_data=event
                )
            
            elif event_type == "postback":
                # User tapped a button
                return ParsedMessage(
                    message_id="postback",
                    user_id=event.get("source", {}).get("userId"),
                    message_type=MessageType.TEXT,
                    content=event.get("postback", {}).get("data", ""),
                    timestamp=datetime.fromtimestamp(event.get("timestamp", 0) / 1000),
                    reply_token=event.get("replyToken"),
                    raw_data=event
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing event: {e}")
            return None
    
    async def handle_webhook(self, request: Request) -> JSONResponse:
        """Handle incoming LINE webhook"""
        body = await request.body()
        body_text = body.decode('utf-8')
        signature = request.headers.get('X-Line-Signature', '')
        
        # Verify signature
        if not self.verify_signature(body_text, signature):
            logger.warning("Invalid signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        try:
            data = json.loads(body_text)
            events = data.get("events", [])
            
            for event in events:
                parsed = self.parse_event(event)
                if parsed:
                    # Get or create session
                    session = self.session_manager.get_session(parsed.user_id)
                    session.add_message("user", parsed.content)
                    
                    # Handle crisis
                    if self.crisis_handler:
                        crisis_result = await self.crisis_handler(parsed, session)
                        if crisis_result.get("is_crisis"):
                            session.crisis_flag = True
                            await self.send_crisis_response(parsed, crisis_result)
                            continue
                    
                    # Handle normal message
                    if self.message_handler:
                        response = await self.message_handler(parsed, session)
                        await self.send_response(parsed.reply_token, response)
                    
                    # Save updated session
                    self.session_manager.save_session(session)
            
            return JSONResponse(content={"status": "ok"})
            
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
    
    async def send_response(self, reply_token: str, response_data: Dict):
        """Send response message"""
        try:
            message_type = response_data.get("type", "text")
            
            if message_type == "text":
                message = TextSendMessage(text=response_data["content"])
            
            elif message_type == "flex":
                flex_content = response_data.get("flex_content")
                alt_text = response_data.get("alt_text", "Message from Nong Unjai")
                message = FlexSendMessage(alt_text=alt_text, contents=flex_content)
            
            elif message_type == "video":
                video_url = self._ensure_full_url(response_data["url"])
                thumbnail_url = self._ensure_full_url(response_data.get("thumbnail", ""))
                logger.info(f"Sending video with URL: {video_url}")
                message = VideoSendMessage(
                    original_content_url=video_url,
                    preview_image_url=thumbnail_url if thumbnail_url else video_url
                )
            
            elif message_type == "image":
                image_url = self._ensure_full_url(response_data["url"])
                thumbnail_url = self._ensure_full_url(response_data.get("thumbnail", ""))
                message = ImageSendMessage(
                    original_content_url=image_url,
                    preview_image_url=thumbnail_url if thumbnail_url else image_url
                )
            
            elif message_type == "quick_reply":
                quick_reply = self.flex_builder.create_quick_reply_buttons(
                    response_data.get("options", [])
                )
                message = TextSendMessage(
                    text=response_data["content"],
                    quick_reply=quick_reply
                )
            
            else:
                message = TextSendMessage(text=response_data.get("content", "..."))
            
            self.line_bot_api.reply_message(reply_token, message)
            
        except LineBotApiError as e:
            logger.error(f"LINE API error: {e}")
        except Exception as e:
            logger.error(f"Error sending response: {e}")
    
    async def send_crisis_response(self, parsed: ParsedMessage, crisis_result: Dict):
        """Send crisis response (Persona 8)"""
        try:
            # Immediate response
            crisis_message = (
                "คุณพี่คะ! หยุดก่อนนะคะ! อุ่นใจอยู่นี่ค่ะ 💙\n\n"
                "อุ่นใจกำลังติดต่อพี่อาสามาช่วยเหลือคุณพี่นะคะ\n"
                "คุณพี่ไม่ได้อยู่คนเดียวค่ะ..."
            )
            
            message = TextSendMessage(text=crisis_message)
            self.line_bot_api.reply_message(parsed.reply_token, message)
            
            # TODO: Trigger human alert via MAAC
            logger.critical(f"CRISIS ALERT for user {parsed.user_id}")
            
        except Exception as e:
            logger.error(f"Error sending crisis response: {e}")
    
    async def push_message(self, user_id: str, message_data: Dict):
        """Push message to user (for proactive nudges)"""
        try:
            message_type = message_data.get("type", "text")
            
            if message_type == "text":
                message = TextSendMessage(text=message_data["content"])
            elif message_type == "flex":
                message = FlexSendMessage(
                    alt_text=message_data.get("alt_text", "..."),
                    contents=message_data["flex_content"]
                )
            else:
                message = TextSendMessage(text=message_data.get("content", "..."))
            
            self.line_bot_api.push_message(user_id, message)
            
        except LineBotApiError as e:
            logger.error(f"LINE API push error: {e}")
    
    def get_user_profile(self, user_id: str) -> Optional[LineUserProfile]:
        """Get LINE user profile"""
        try:
            profile = self.line_bot_api.get_profile(user_id)
            return LineUserProfile(
                user_id=profile.user_id,
                display_name=profile.display_name,
                picture_url=profile.picture_url,
                status_message=profile.status_message,
                language="th"
            )
        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return None
    
    def set_message_handler(self, handler: Callable):
        """Set message handler callback"""
        self.message_handler = handler
    
    def set_crisis_handler(self, handler: Callable):
        """Set crisis handler callback"""
        self.crisis_handler = handler


# FastAPI app factory
def create_app(gateway: LineGateway) -> FastAPI:
    """Create FastAPI app with LINE webhook endpoint"""
    
    app = FastAPI(title="Nong Unjai LINE Gateway")
    
    @app.post("/webhook")
    async def webhook(request: Request):
        """LINE webhook endpoint"""
        return await gateway.handle_webhook(request)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "mode": "coordinated",
            "features": {
                "orchestrator_gateway_coordination": True,
                "agent_communication_protocol": True,
                "search_specialist": True,
                "journey_architect": True,
                "front_desk": True
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @app.get("/coordination/status")
    async def coordination_status():
        """Check coordination system status"""
        try:
            from coordination_protocol import get_coordinator
            
            coord = get_coordinator()
            agents = coord.registry.get_all_active()
            sessions = coord.get_all_sessions()
            
            return {
                "status": "active",
                "coordination": "enabled",
                "registered_agents": agents,
                "agent_count": len(agents),
                "active_sessions": len(sessions),
                "communication_protocol": "AgentBus",
                "gateway_orchestrator_bridge": "connected"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "coordination": "check_failed"
            }
    
    @app.get("/stats")
    async def get_stats():
        """Get gateway statistics"""
        # TODO: Implement stats
        return {"total_messages": 0, "active_sessions": 0}
    
    @app.get("/debug/sessions")
    async def debug_sessions():
        """Debug: Show all sessions with Q&A history"""
        from session_debugger import get_debugger
        
        debugger = get_debugger()
        sessions = debugger.get_all_sessions()
        
        result = {
            "total_sessions": len(sessions),
            "base_url": gateway.base_url,
            "sessions": {}
        }
        
        for sid, session in sessions.items():
            result["sessions"][sid] = {
                "user_id": session.user_id,
                "start_time": session.start_time,
                "last_activity": session.last_activity,
                "qa_count": session.qa_count,
                "qa_history": [
                    {
                        "timestamp": qa.timestamp,
                        "question": qa.question,
                        "raw_clip_url": qa.raw_clip_url,
                        "full_clip_url": qa.full_clip_url,
                        "score": qa.score,
                        "decision": qa.decision,
                        "url_correct": qa.full_clip_url.startswith(gateway.base_url)
                    }
                    for qa in session.qa_history
                ]
            }
        
        return result
    
    return app


# Example usage
if __name__ == "__main__":
    import uvicorn
    
    # Initialize gateway
    gateway = LineGateway()
    
    # Set up handlers
    async def message_handler(parsed: ParsedMessage, session: UserSession) -> Dict:
        """Example message handler"""
        # This would integrate with NLP Processor
        return {
            "type": "text",
            "content": f"Echo: {parsed.content}"
        }
    
    async def crisis_handler(parsed: ParsedMessage, session: UserSession) -> Dict:
        """Example crisis handler"""
        # This would integrate with CrisisDetector
        return {"is_crisis": False}
    
    gateway.set_message_handler(message_handler)
    gateway.set_crisis_handler(crisis_handler)
    
    # Create and run app
    app = create_app(gateway)
    uvicorn.run(app, host="0.0.0.0", port=8000)
