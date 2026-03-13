"""
LINE Gateway Service Entry Point - Full Coordination Protocol
เปิดใช้งาน Orchestrator/Gateway Coordination และ Communication Protocol
"""
import os
import sys
import asyncio

# เพิ่ม path
sys.path.insert(0, '/app/modules')

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GatewayEntrypoint")

# Import coordination system
from coordination_protocol import get_coordinator, AgentTaskType
from module_4_line_gateway import LineGateway, ParsedMessage, UserSession, create_app

# Import Agents
from line_orchestrator import SearchSpecialistConnector, JourneyArchitectDecision
from pinecone_connector import get_connector as get_pinecone

# Import Flex Message Templates
from flex_templates import FlexMessageBuilder

# Import Auto-Tool
try:
    sys.path.insert(0, '/app/tools')
    from search_specialist_tool import SearchSpecialistTool
    AUTO_TOOL_AVAILABLE = True
except ImportError:
    AUTO_TOOL_AVAILABLE = False
    logger.warning("⚠️  Search Specialist Auto-Tool not available")


class CoordinatedLINEGateway:
    """
    LINE Gateway with Full Agent Coordination
    """
    
    def __init__(self):
        self.line_gateway = LineGateway()
        self.coordinator = get_coordinator()
        self.search_specialist = SearchSpecialistConnector()
        self.journey_architect = JourneyArchitectDecision()
        
        # Register agents with coordinator
        self._register_agents()
        
        # Setup message handler
        self.line_gateway.set_message_handler(self._handle_message)
        
        logger.info("="*60)
        logger.info("🚀 COORDINATED LINE GATEWAY")
        logger.info("="*60)
        logger.info("✅ Search Specialist Agent: ACTIVE")
        logger.info("✅ Journey Architect Agent: ACTIVE")
        logger.info("✅ Front-Desk Agent: ACTIVE")
        logger.info("✅ Communication Protocol: ENABLED")
        logger.info("✅ Gateway-Orchestrator Coordination: ENABLED")
        logger.info("="*60)
    
    def _register_agents(self):
        """ลงทะเบียน Agents กับ Coordinator"""
        
        # Search Specialist with Auto-Tool (Hybrid Search v2.0)
        async def search_handler(payload):
            query = payload.get("query", "")
            logger.info(f"🔍 Search Specialist Hybrid Search: {query[:50]}...")
            
            try:
                # Use Auto-Tool v2.0 with Hybrid Search
                if AUTO_TOOL_AVAILABLE:
                    tool = SearchSpecialistTool()
                    result = tool.hybrid_search(query)  # ใช้ hybrid_search แทน
                    
                    logger.info(f"✅ Hybrid Search Complete:")
                    logger.info(f"   Text results: {result.get('total_text', 0)}")
                    logger.info(f"   Video results: {result.get('total_videos', 0)}")
                    logger.info(f"   High Priority (score>0.80): {len(result.get('high_priority_videos', []))}")
                    
                    # กฎเหล็ก: ถ้ามี high priority videos ต้อง log เตือน
                    if result.get('has_high_priority'):
                        logger.info(f"🚨 IRON RULE: High priority videos detected - MUST send to Journey Architect!")
                else:
                    # Fallback to original method
                    videos = await self.search_specialist.search_pinecone_by_text(query)
                    result = {
                        "text_results": [],
                        "video_results": videos,
                        "high_priority_videos": [],
                        "has_high_priority": False
                    }
                
                return result
                
            except Exception as e:
                logger.error(f"❌ Search Specialist error: {e}")
                import traceback
                traceback.print_exc()
                return {
                    "text_results": [],
                    "video_results": [],
                    "high_priority_videos": [],
                    "has_high_priority": False,
                    "error": str(e)
                }
        
        self.coordinator.registry.register(
            "search_specialist", 
            search_handler, 
            ["search", "pinecone", "video", "auto_tool", "hybrid_search", "memory_search"]
        )
        
        if AUTO_TOOL_AVAILABLE:
            logger.info("✅ Search Specialist Auto-Tool v2.0: ENABLED")
            logger.info("   Features: Hybrid Search (Text + Video)")
            logger.info("   Iron Rule: Score > 0.80 → Must send metadata")
        else:
            logger.info("⚠️  Search Specialist Auto-Tool: DISABLED (fallback mode)")
        
        # Journey Architect (with Iron Rule support)
        def decide_handler(payload):
            message = payload.get("message", "")
            search_results = payload.get("search_results", {})
            
            # รับข้อมูลจาก Hybrid Search
            video_results = search_results.get("video_results", [])
            text_results = search_results.get("text_results", [])
            high_priority_videos = search_results.get("high_priority_videos", [])
            has_high_priority = search_results.get("has_high_priority", False)
            
            logger.info(f"🎯 Journey Architect analyzing:")
            logger.info(f"   Text results: {len(text_results)}")
            logger.info(f"   Video results: {len(video_results)}")
            logger.info(f"   High priority: {len(high_priority_videos)}")
            
            # กฎเหล็ก: ถ้ามี high priority videos (score > 0.80) ต้องส่ง video เสมอ
            if has_high_priority and high_priority_videos:
                top_video = high_priority_videos[0]
                logger.info(f"🚨 IRON RULE APPLIED: High priority video detected (score: {top_video.get('score', 0):.3f})")
                return {
                    "decision": "video_package",
                    "confidence": 0.95,
                    "reason": "iron_rule_high_priority",
                    "selected_video": top_video,
                    "all_videos": video_results,
                    "text_content": text_results[0] if text_results else None
                }
            
            # ถ้าไม่มี high priority ใช้ logic ปกติ
            if video_results and video_results[0].get("score", 0) > 0.75:
                return {
                    "decision": "video_package",
                    "confidence": 0.8,
                    "selected_video": video_results[0],
                    "all_videos": video_results
                }
            elif video_results:
                return {
                    "decision": "video_nudge",
                    "confidence": 0.6,
                    "selected_video": video_results[0],
                    "all_videos": video_results
                }
            else:
                return {
                    "decision": "text_only",
                    "confidence": 0.9,
                    "text_content": text_results[0] if text_results else None
                }
        
        self.coordinator.registry.register(
            "journey_architect",
            decide_handler,
            ["decide", "routing", "strategy"]
        )
        
        # Front-Desk (with Hybrid Search support)
        async def respond_handler(payload):
            message = payload.get("message", "")
            decision = payload.get("decision", {})
            search_results = payload.get("search_results", {})
            
            decision_type = decision.get("decision", "text_only")
            selected_video = decision.get("selected_video")
            text_content = decision.get("text_content")
            reason = decision.get("reason", "")
            
            # รับ videos จากหลายแหล่ง
            all_videos = decision.get("all_videos", [])
            if not all_videos:
                all_videos = search_results.get("video_results", [])
            
            logger.info(f"🎙️ Front-Desk: decision={decision_type}, reason={reason}")
            
            # กฎเหล็ก: ถ้าเป็น iron_rule ให้ log พิเศษ
            if reason == "iron_rule_high_priority":
                logger.info(f"🚨 Front-Desk: Processing IRON RULE response")
            
            if decision_type in ["video_package", "video_nudge"] and selected_video:
                video = selected_video
                logger.info(f"🎬 Front-Desk: Preparing video delivery request")
                
                # ✅ CORRECT: Front-Desk only returns video METADATA
                # Media Delivery Agent will build the Flex Message
                response = {
                    "type": "video",  # Not "flex" - let Media Delivery build it
                    "video_data": {
                        "title": video.get("title", "คลิปหนุนใจ"),
                        "full_url": video.get("full_url", ""),
                        "clip_url": video.get("clip_url", ""),
                        "thumbnail": video.get("thumbnail", ""),
                        "video_url": video.get("video_url", ""),
                        "score": video.get("score", 0),
                        "transcript": video.get("transcript", "")[:100],
                        "quiz": video.get("quiz"),
                        "quiz_available": video.get("quiz") is not None,
                    },
                    "alt_text": f"🎬 {video.get('title', 'คลิปหนุนใจ')}",
                    "metadata": {
                        "iron_rule_applied": reason == "iron_rule_high_priority",
                        "decision_type": decision_type
                    }
                }
                
                # ถ้ามี text content ด้วย ให้เติมข้อมูลเพิ่ม
                if text_content:
                    response["text_supplement"] = text_content.get("content", "")[:200]
                
                return response
                
            elif text_content:
                # ถ้ามี text result แต่ไม่มี video
                logger.info(f"💬 Front-Desk: Sending text response from MEMORY.md")
                return {
                    "type": "text",
                    "content": f"{text_content.get('content', '')[:500]}...\n\n💕 จากน้องอุ่นใจ"
                }
            else:
                logger.info(f"💬 Front-Desk: Sending default text response")
                return {
                    "type": "text",
                    "content": f"สวัสดีค่ะคุณพี่! อุ่นใจได้รับข้อความ: \"{message[:30]}...\" ค่ะ 💕"
                }
        
        self.coordinator.registry.register(
            "front_desk",
            respond_handler,
            ["respond", "text", "flex"]
        )
        
        # Media Delivery Agent - ส่งมอบสื่อ (Flex Messages)
        async def deliver_handler(payload):
            """
            🎬 Media Delivery Agent (Squad 4: Content Integrity & Delivery)
            
            Task: สร้างและส่งมอบสื่อ (Flex Messages) ให้กับผู้ใช้
            
            Responsibility:
            - รับ video metadata จาก Front-Desk
            - สร้าง Flex Message ด้วย FlexMessageBuilder
            - ตรวจสอบความถูกต้องของเนื้อหาก่อนส่ง
            """
            response = payload.get("response", {})
            media_type = response.get("type")
            
            logger.info(f"🎬 Media Delivery: Building {media_type} message")
            
            try:
                if media_type == "video":
                    # ✅ CORRECT: Media Delivery builds Flex Message from video_data
                    video_data = response.get("video_data", {})
                    decision_type = response.get("metadata", {}).get("decision_type", "video_package")
                    
                    # Build Flex Message using FlexMessageBuilder
                    if decision_type == "video_nudge":
                        flex_content = FlexMessageBuilder.create_video_nudge(video_data)
                        logger.info("✅ Media Delivery: Built video NUDGE flex message")
                    else:
                        flex_content = FlexMessageBuilder.create_video_card(video_data)
                        logger.info("✅ Media Delivery: Built VIDEO CARD flex message")
                    
                    # Verify the flex content is valid
                    if flex_content.get("type") == "bubble":
                        logger.info("✅ Media Delivery: Flex bubble validated")
                    else:
                        logger.warning("⚠️  Media Delivery: Unexpected flex type")
                    
                    return {
                        "status": "delivered",
                        "type": "flex",
                        "content": flex_content,
                        "alt_text": response.get("alt_text", "🎬 คลิปหนุนใจ"),
                        "metadata": response.get("metadata", {})
                    }
                
                elif media_type == "text":
                    logger.info("✅ Media Delivery: Text message ready")
                    return {
                        "status": "delivered",
                        "type": "text",
                        "content": response.get("content", "")
                    }
                
                else:
                    logger.warning(f"⚠️  Media Delivery: Unknown type {media_type}")
                    return {
                        "status": "error",
                        "error": f"Unknown media type: {media_type}"
                    }
                    
            except Exception as e:
                logger.error(f"❌ Media Delivery error: {e}")
                import traceback
                traceback.print_exc()
                return {
                    "status": "error",
                    "error": str(e)
                }
        
        self.coordinator.registry.register(
            "media_delivery",
            deliver_handler,
            ["deliver", "flex", "video", "line"]
        )
        
        logger.info(f"✅ Registered {len(self.coordinator.registry.get_all_active())} agents")
        logger.info("   - Search Specialist (Hybrid Search)")
        logger.info("   - Journey Architect (Decision)")
        logger.info("   - Front-Desk (Response - returns video metadata)")
        logger.info("   - Media Delivery (Flex Message BUILDING & Delivery)")
    
    async def _handle_message(self, parsed: ParsedMessage, session: UserSession) -> dict:
        """
        จัดการข้อความ - ใช้ Coordination Protocol
        """
        try:
            logger.info(f"📩 New message from {parsed.user_id}: {parsed.content[:50]}...")
            
            # ใช้ Coordinator ประสานงาน
            response = await self.coordinator.coordinate_request(
                user_id=parsed.user_id,
                message=parsed.content
            )
            
            logger.info(f"✅ Response ready: {response.get('type', 'unknown')}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "type": "text",
                "content": "ขออภัยค่ะคุณพี่ อุ่นใจมีปัญหาเล็กน้อย กรุณาลองใหม่อีกครั้งนะคะ 🙏"
            }
    
    async def initialize(self):
        """เริ่มต้นระบบ"""
        await self.coordinator.start()
        logger.info("✅ Gateway initialized and ready")
    
    def get_app(self):
        """Get FastAPI app"""
        return create_app(self.line_gateway)


# Global instance
coordinated_gateway = None

async def get_gateway():
    """Get or create gateway"""
    global coordinated_gateway
    if coordinated_gateway is None:
        coordinated_gateway = CoordinatedLINEGateway()
        await coordinated_gateway.initialize()
    return coordinated_gateway


if __name__ == "__main__":
    import uvicorn
    
    async def main():
        # Initialize gateway
        gateway = await get_gateway()
        app = gateway.get_app()
        
        # Get config
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        
        logger.info(f"🚀 Starting Coordinated Gateway on {host}:{port}")
        
        # Run server
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    
    # Run
    asyncio.run(main())
