"""
🌐 Nong Unjai Gateway - Main Entry Point
เชื่อมต่อ LINE API เข้ากับ Swarm Orchestrator
"""

import os
import sys
import asyncio
import json
from typing import Dict, Optional, Any
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NongUnjaiGateway")


class NongUnjaiGateway:
    """
    🌐 Main Gateway - ประตูหน้าบ้านของระบบ
    รับข้อความจาก LINE และส่งต่อไปยัง Swarm Orchestrator
    """
    
    def __init__(self):
        self.orchestrator = None
        self.session_manager = None
        self.initialized = False
        
        # Config
        self.base_url = "https://nongaunjai.febradio.org"
        self.api_port = int(os.getenv("API_PORT", "8000"))
        
        logger.info("🌐 NongUnjaiGateway initializing...")
    
    async def initialize(self):
        """เริ่มต้นระบบทั้งหมด"""
        if self.initialized:
            return
        
        logger.info("=" * 60)
        logger.info("🚀 INITIALIZING NONG UNJAI SYSTEM")
        logger.info("=" * 60)
        
        # 1. เริ่มต้น Orchestrator
        from modules.swarm_orchestrator import get_orchestrator, AgentRole, BaseAgent
        from modules.pinecone_connector import get_connector
        
        self.orchestrator = get_orchestrator()
        
        # 2. สร้างและลงทะเบียน Agents จริง
        
        ## Search Specialist
        from activate_swarm import SearchSpecialistAgent
        search_agent = SearchSpecialistAgent()
        
        class SearchAgentWrapper(BaseAgent):
            def __init__(self, real_agent):
                super().__init__(AgentRole.SEARCH_SPECIALIST)
                self.real_agent = real_agent
            
            async def process(self, context):
                """ค้นหาข้อมูล"""
                query = context.get('message', '')
                user_id = context.get('user_id', '')
                
                logger.info(f"🔍 Search Specialist searching: {query[:30]}...")
                
                result = await self.real_agent.search(query, user_id)
                
                context['search_results'] = result
                context['has_videos'] = result.get('has_highlights', False)
                context['video_count'] = len(result.get('video_results', []))
                
                # ถ้ามีวิดีโอ ส่งข้อมูลไปให้ Journey Architect
                if context['has_videos']:
                    await self.send_to(
                        AgentRole.JOURNEY_ARCHITECT,
                        self.orchestrator.bus.__class__.__name__,
                        {"videos": result['video_results']}
                    )
                
                return context
        
        search_wrapper = SearchAgentWrapper(search_agent)
        
        ## Journey Architect
        class JourneyArchitectAgent(BaseAgent):
            def __init__(self):
                super().__init__(AgentRole.JOURNEY_ARCHITECT)
            
            async def process(self, context):
                """ตัดสินใจเลือกรูปแบบการตอบ"""
                has_videos = context.get('has_videos', False)
                r_score = context.get('r_score', 0)
                
                logger.info(f"🎯 Journey Architect deciding (r_score={r_score}, videos={has_videos})")
                
                # 3-Filter Decision
                if r_score < 30:
                    decision = "text_only"
                elif has_videos and r_score >= 60:
                    decision = "video_package"
                elif has_videos:
                    decision = "video_nudge"
                else:
                    decision = "text_only"
                
                context['decision'] = decision
                context['persona_id'] = self._select_persona(context)
                
                logger.info(f"  Decision: {decision}, Persona: {context['persona_id']}")
                
                return context
            
            def _select_persona(self, context):
                """เลือก Persona ตาม context"""
                message = context.get('message', '').lower()
                
                # ตรวจสอบ SOS keywords
                sos_words = ['อยากตาย', 'ไม่อยากอยู่', 'ฆ่าตัว']
                if any(w in message for w in sos_words):
                    return 8  # SOS Persona
                
                # ตรวจสอบอารมณ์
                if any(w in message for w in ['เศร้า', 'เหนื่อย', 'ท้อ']):
                    return 2  # Healer Persona
                
                if any(w in message for w in ['สวัสดี', 'หวัดดี']):
                    return 6  # Passive Watcher
                
                # Default
                return 1  # Intellectual
        
        journey_agent = JourneyArchitectAgent()
        
        ## Front-Desk Agent
        class FrontDeskAgent(BaseAgent):
            def __init__(self):
                super().__init__(AgentRole.FRONT_DESK)
                self.personas = self._load_personas()
            
            def _load_personas(self):
                """โหลด 12 Personas"""
                return {
                    1: "พี่สาวสายปัญญา",
                    2: "เพื่อนสาวสายเยียวยา",
                    3: "น้องสาวสายกิจกรรม",
                    4: "ที่ปรึกษาสายเป๊ะ",
                    5: "เพื่อนสนิทสายอธิษฐาน",
                    6: "น้องอุ่นใจสายห่วงใย",
                    7: "เพื่อนสาวจอมสงสัย",
                    8: "หน่วยกู้ใจสายด่วน",
                    9: "ตัวตึงสายพระพร",
                    10: "พี่สาวสายพักสงบ",
                    11: "น้องน้อยสายเก็บแต้ม",
                    12: "เพื่อนบ้านแสนดี"
                }
            
            async def process(self, context):
                """สร้างข้อความตอบกลับ"""
                decision = context.get('decision', 'text_only')
                persona_id = context.get('persona_id', 1)
                search_results = context.get('search_results', {})
                videos = search_results.get('video_results', [])
                
                persona_name = self.personas.get(persona_id, "น้องอุ่นใจ")
                logger.info(f"🎭 Front-Desk using Persona {persona_id}: {persona_name}")
                
                # สร้าง response
                response = {
                    "type": decision,
                    "persona_id": persona_id,
                    "persona_name": persona_name,
                    "text": self._generate_text(context),
                    "videos": [],
                    "quick_replies": []
                }
                
                if decision in ["video_nudge", "video_package"] and videos:
                    response['videos'] = [{
                        "clip_url": v['clip_url'],
                        "transcript": v['transcript'][:100] + "...",
                        "reason": v['reason']
                    } for v in videos[:2]]
                    
                    # Quick replies for video
                    response['quick_replies'] = [
                        {"label": "ดูวิดีโอเลย", "action": "watch_video"},
                        {"label": "ขอคำตอบก่อน", "action": "text_first"}
                    ]
                
                context['response'] = response
                
                # Broadcast response ready
                await self.broadcast("response_ready", {
                    "user_id": context.get('user_id'),
                    "response": response
                })
                
                return context
            
            def _generate_text(self, context):
                """สร้างข้อความตาม Persona"""
                persona_id = context.get('persona_id', 1)
                message = context.get('message', '')
                
                # Simple response templates
                responses = {
                    1: f"คุณพี่คะ สำหรับคำถามนี้ อุ่นใจขอแบ่งปันความรู้นะคะ 🙏",
                    2: f"คุณพี่ขา... อุ่นใจเข้าใจความรู้สึกนี้นะคะ 💕",
                    6: f"สวัสดีค่ะคุณพี่ อุ่นใจคิดถึงคุณพี่นะคะ 🌸",
                    8: f"คุณพี่คะ! อุ่นใจอยู่ตรงนี้ค่ะ 🛑 หยุดก่อนนะคะ"
                }
                
                return responses.get(persona_id, "สวัสดีค่ะคุณพี่ อุ่นใจยินดีช่วยเหลือค่ะ 💕")
        
        front_desk = FrontDeskAgent()
        
        ## Sentinel Agent (Safety)
        class SentinelAgent(BaseAgent):
            def __init__(self):
                super().__init__(AgentRole.SENTINEL)
                self.sos_keywords = [
                    'อยากตาย', 'ไม่อยากอยู่', 'ลาก่อน', 'ฆ่าตัวตาย',
                    'ไม่ไหวแล้ว', 'มืดแปดด้าน', 'ไม่มีทางออก'
                ]
            
            async def process(self, context):
                """ตรวจสอบความปลอดภัย"""
                message = context.get('message', '').lower()
                
                # Check SOS
                is_crisis = any(kw in message for kw in self.sos_keywords)
                
                if is_crisis:
                    logger.warning(f"🚨 CRISIS DETECTED: {message[:50]}...")
                    context['is_crisis'] = True
                    context['persona_id'] = 8  # SOS Persona
                    context['alert_sentinel'] = True
                    
                    # Alert other agents
                    await self.broadcast("crisis_detected", {
                        "user_id": context.get('user_id'),
                        "message": message
                    })
                else:
                    context['is_crisis'] = False
                
                return context
        
        sentinel = SentinelAgent()
        
        # 3. ลงทะเบียน workflow
        logger.info("\n📋 Registered Workflows:")
        for name, agents in self.orchestrator.workflows.items():
            logger.info(f"  - {name}: {[a.value for a in agents]}")
        
        self.initialized = True
        logger.info("\n✅ NongUnjaiGateway initialized successfully!")
    
    async def process_message(self, user_id: str, message: str, 
                             r_score: int = 50) -> Dict:
        """
        ประมวลผลข้อความจากผู้ใช้
        
        Flow:
        1. Sentinel ตรวจสอบความปลอดภัย
        2. Search Specialist ค้นหาข้อมูล
        3. Journey Architect ตัดสินใจ
        4. Front-Desk สร้างคำตอบ
        """
        if not self.initialized:
            await self.initialize()
        
        logger.info(f"\n📩 Processing message from {user_id}: {message[:50]}...")
        
        # Execute workflow
        result = await self.orchestrator.execute_workflow(
            "user_message",
            {
                "user_id": user_id,
                "message": message,
                "r_score": r_score,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return result.get('response', {})
    
    def get_system_status(self) -> Dict:
        """ดูสถานะระบบทั้งหมด"""
        if not self.orchestrator:
            return {"status": "not_initialized"}
        
        return {
            "status": "operational" if self.initialized else "initializing",
            "gateway": "online",
            "agents": self.orchestrator.get_agent_status(),
            "base_url": self.base_url,
            "api_port": self.api_port
        }


# 🚀 Singleton
gateway_instance: Optional[NongUnjaiGateway] = None

def get_gateway() -> NongUnjaiGateway:
    """Get gateway singleton"""
    global gateway_instance
    if gateway_instance is None:
        gateway_instance = NongUnjaiGateway()
    return gateway_instance


# 🧪 Test
async def test_gateway():
    """ทดสอบ Gateway"""
    print("=" * 70)
    print("🌐 TESTING NONG UNJAI GATEWAY")
    print("=" * 70)
    
    gateway = get_gateway()
    await gateway.initialize()
    
    # Test messages
    test_messages = [
        ("user_001", "สวัสดีค่ะ", 30),
        ("user_002", "อยากรู้เรื่องการให้อภัย", 70),
        ("user_003", "เหนื่อยจังเลย", 40),
    ]
    
    print("\n📨 Testing message processing:")
    print("-" * 70)
    
    for user_id, message, r_score in test_messages:
        print(f"\n👤 User: {user_id}")
        print(f"   Message: '{message}'")
        print(f"   R-Score: {r_score}")
        
        response = await gateway.process_message(user_id, message, r_score)
        
        print(f"\n   🤖 Bot Response:")
        print(f"      Type: {response.get('type')}")
        print(f"      Persona: {response.get('persona_name')} (ID: {response.get('persona_id')})")
        print(f"      Text: {response.get('text')}")
        
        if response.get('videos'):
            print(f"      Videos: {len(response['videos'])} clip(s)")
            for v in response['videos']:
                print(f"        - {v['clip_url']}")
    
    print("\n" + "=" * 70)
    print("✅ Gateway tests complete!")
    print("=" * 70)
    
    # Show status
    status = gateway.get_system_status()
    print(f"\n📊 System Status: {status['status']}")
    print(f"   Base URL: {status['base_url']}")


if __name__ == "__main__":
    asyncio.run(test_gateway())
