"""
🎯 Nong Unjai Swarm Orchestrator & Inter-Agent Communication Protocol
ระบบประสานงานและโปรโตคอลการสื่อสารระหว่าง Agents
"""

import os
import sys
import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SwarmOrchestrator")


class MessageType(Enum):
    """ประเภทข้อความระหว่าง Agents"""
    COMMAND = "command"           # คำสั่ง
    QUERY = "query"               # คำถาม/ขอข้อมูล
    RESPONSE = "response"         # ตอบกลับ
    EVENT = "event"               # เหตุการณ์
    BROADCAST = "broadcast"       # ประกาศทั่วไป
    ALERT = "alert"               # แจ้งเตือน
    HANDOFF = "handoff"           # ส่งต่องาน


class AgentRole(Enum):
    """บทบาทของ Agents"""
    ARCHIVIST = "archivist"
    SEARCH_SPECIALIST = "search_specialist"
    JOURNEY_ARCHITECT = "journey_architect"
    SENTINEL = "sentinel"
    FRONT_DESK = "front_desk"
    ACADEMY = "academy"
    MEDIA_DELIVERY = "media_delivery"
    AUDITOR = "auditor"
    REWARD_MANAGER = "reward_manager"
    MAAC_SYNC = "maac_sync"
    INSIGHTS = "insights"
    TREND_PREDICTOR = "trend_predictor"
    LOCAL_CONNECTOR = "local_connector"
    SYSTEM_TUNER = "system_tuner"
    AUTO_QA = "auto_qa"


@dataclass
class AgentMessage:
    """
    📨 Message Protocol สำหรับสื่อสารระหว่าง Agents
    """
    msg_id: str
    msg_type: MessageType
    from_agent: AgentRole
    to_agent: Optional[AgentRole]  # None = broadcast
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 5  # 1-10 (1 = highest)
    correlation_id: Optional[str] = None  # สำหรับติดตาม thread
    
    def to_dict(self) -> Dict:
        return {
            "msg_id": self.msg_id,
            "msg_type": self.msg_type.value,
            "from_agent": self.from_agent.value,
            "to_agent": self.to_agent.value if self.to_agent else None,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "correlation_id": self.correlation_id
        }
    
    @classmethod
    def create(cls, from_agent: AgentRole, msg_type: MessageType, 
               payload: Dict, to_agent: Optional[AgentRole] = None,
               priority: int = 5, correlation_id: Optional[str] = None) -> 'AgentMessage':
        import uuid
        return cls(
            msg_id=str(uuid.uuid4())[:8],
            msg_type=msg_type,
            from_agent=from_agent,
            to_agent=to_agent,
            payload=payload,
            priority=priority,
            correlation_id=correlation_id
        )


class AgentBus:
    """
    🚌 Agent Communication Bus
    ระบบสื่อสารกลางสำหรับ Agents ทั้งหมด
    """
    
    def __init__(self):
        self.subscribers: Dict[AgentRole, List[Callable]] = {}
        self.message_history: List[AgentMessage] = []
        self.max_history = 1000
        logger.info("🚌 AgentBus initialized")
    
    def subscribe(self, agent: AgentRole, handler: Callable):
        """ลงทะเบียนรับข้อความ"""
        if agent not in self.subscribers:
            self.subscribers[agent] = []
        self.subscribers[agent].append(handler)
        logger.info(f"📬 {agent.value} subscribed to AgentBus")
    
    def unsubscribe(self, agent: AgentRole, handler: Callable):
        """ยกเลิกการลงทะเบียน"""
        if agent in self.subscribers and handler in self.subscribers[agent]:
            self.subscribers[agent].remove(handler)
    
    async def publish(self, message: AgentMessage):
        """ส่งข้อความไปยัง Agents"""
        # Save to history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
        
        # Route to target agent(s)
        if message.to_agent:
            # Direct message
            if message.to_agent in self.subscribers:
                for handler in self.subscribers[message.to_agent]:
                    try:
                        await handler(message)
                    except Exception as e:
                        logger.error(f"❌ Error handling message to {message.to_agent}: {e}")
        else:
            # Broadcast to all except sender
            for agent, handlers in self.subscribers.items():
                if agent != message.from_agent:
                    for handler in handlers:
                        try:
                            await handler(message)
                        except Exception as e:
                            logger.error(f"❌ Error broadcasting to {agent}: {e}")
    
    def get_history(self, agent: Optional[AgentRole] = None, 
                   msg_type: Optional[MessageType] = None,
                   limit: int = 50) -> List[AgentMessage]:
        """ดูประวัติข้อความ"""
        results = self.message_history
        
        if agent:
            results = [m for m in results if m.to_agent == agent or m.from_agent == agent]
        
        if msg_type:
            results = [m for m in results if m.msg_type == msg_type]
        
        return results[-limit:]


class SwarmOrchestrator:
    """
    🎯 Master Orchestrator
    ประสานงานและควบคุมการทำงานของ Agents ทั้งหมด
    """
    
    def __init__(self):
        self.bus = AgentBus()
        self.agents: Dict[AgentRole, Any] = {}
        self.workflows: Dict[str, List[AgentRole]] = {}
        self.active_sessions: Dict[str, Dict] = {}
        self._setup_workflows()
        logger.info("🎯 SwarmOrchestrator initialized")
    
    def _setup_workflows(self):
        """กำหนด Workflow มาตรฐาน"""
        self.workflows = {
            "user_message": [
                AgentRole.SENTINEL,        # 1. ตรวจสอบความปลอดภัย
                AgentRole.SEARCH_SPECIALIST, # 2. ค้นหาข้อมูล
                AgentRole.JOURNEY_ARCHITECT, # 3. ตัดสินใจ
                AgentRole.FRONT_DESK       # 4. ตอบกลับ
            ],
            "video_request": [
                AgentRole.SEARCH_SPECIALIST,
                AgentRole.JOURNEY_ARCHITECT,
                AgentRole.MEDIA_DELIVERY,
                AgentRole.ACADEMY
            ],
            "crisis_detected": [
                AgentRole.SENTINEL,
                AgentRole.FRONT_DESK,      # Persona 8
                AgentRole.LOCAL_CONNECTOR   # เรียกอาสา
            ],
            "daily_nudge": [
                AgentRole.INSIGHTS,
                AgentRole.JOURNEY_ARCHITECT,
                AgentRole.FRONT_DESK
            ]
        }
    
    def register_agent(self, role: AgentRole, agent_instance: Any):
        """ลงทะเบียน Agent เข้าระบบ"""
        self.agents[role] = agent_instance
        self.bus.subscribe(role, self._create_handler(role))
        logger.info(f"✅ {role.value} registered with Orchestrator")
    
    def _create_handler(self, role: AgentRole) -> Callable:
        """สร้าง message handler สำหรับ Agent"""
        async def handler(message: AgentMessage):
            agent = self.agents.get(role)
            if agent and hasattr(agent, 'handle_message'):
                await agent.handle_message(message)
        return handler
    
    async def execute_workflow(self, workflow_name: str, 
                              initial_payload: Dict,
                              session_id: str = None) -> Dict:
        """
        🔄 รัน Workflow ตามลำดับ
        
        Example:
            result = await orchestrator.execute_workflow(
                "user_message",
                {"user_id": "123", "message": "สวัสดี"}
            )
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow = self.workflows[workflow_name]
        context = initial_payload.copy()
        
        logger.info(f"🔄 Executing workflow '{workflow_name}' with {len(workflow)} steps")
        
        for step, agent_role in enumerate(workflow, 1):
            agent = self.agents.get(agent_role)
            if not agent:
                logger.warning(f"⚠️  Agent {agent_role} not found, skipping")
                continue
            
            logger.info(f"  Step {step}/{len(workflow)}: {agent_role.value}")
            
            # Execute agent task
            try:
                if hasattr(agent, 'process'):
                    context = await agent.process(context)
                elif hasattr(agent, 'execute'):
                    context = await agent.execute(context)
            except Exception as e:
                logger.error(f"❌ Error in {agent_role}: {e}")
                context['error'] = str(e)
                context['failed_at'] = agent_role.value
                break
        
        return context
    
    async def send_command(self, from_agent: AgentRole, to_agent: AgentRole,
                          command: str, data: Dict = None):
        """ส่งคำสั่งไปยัง Agent อื่น"""
        message = AgentMessage.create(
            from_agent=from_agent,
            to_agent=to_agent,
            msg_type=MessageType.COMMAND,
            payload={"command": command, "data": data or {}}
        )
        await self.bus.publish(message)
    
    async def broadcast_event(self, from_agent: AgentRole, 
                             event_name: str, data: Dict = None):
        """ประกาศเหตุการณ์ไปยังทุก Agent"""
        message = AgentMessage.create(
            from_agent=from_agent,
            to_agent=None,  # Broadcast
            msg_type=MessageType.EVENT,
            payload={"event": event_name, "data": data or {}}
        )
        await self.bus.publish(message)
    
    def get_agent_status(self) -> Dict[str, str]:
        """ดูสถานะ Agents ทั้งหมด"""
        return {
            role.value: "registered" if role in self.agents else "not_registered"
            for role in AgentRole
        }


# 🎯 Singleton Instance
_orchestrator: Optional[SwarmOrchestrator] = None

def get_orchestrator() -> SwarmOrchestrator:
    """Get orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SwarmOrchestrator()
    return _orchestrator


# 🚀 Base Agent Class สำหรับทุก Agent
class BaseAgent:
    """
    🎭 Base Class สำหรับทุก Agent
    """
    
    def __init__(self, role: AgentRole):
        self.role = role
        self.orchestrator = get_orchestrator()
        self.orchestrator.register_agent(role, self)
        self.state: Dict = {}
        logger.info(f"🎭 {role.value} initialized")
    
    async def handle_message(self, message: AgentMessage):
        """รับข้อความจาก AgentBus"""
        logger.info(f"📨 {self.role.value} received: {message.msg_type.value} from {message.from_agent.value}")
        
        if message.msg_type == MessageType.COMMAND:
            await self.handle_command(message.payload.get("command"), message.payload.get("data", {}))
        elif message.msg_type == MessageType.QUERY:
            response = await self.handle_query(message.payload)
            # Send response back
            await self.orchestrator.bus.publish(AgentMessage.create(
                from_agent=self.role,
                to_agent=message.from_agent,
                msg_type=MessageType.RESPONSE,
                payload=response,
                correlation_id=message.correlation_id
            ))
    
    async def handle_command(self, command: str, data: Dict):
        """Override ใน subclass"""
        pass
    
    async def handle_query(self, query: Dict) -> Dict:
        """Override ใน subclass"""
        return {}
    
    async def send_to(self, target: AgentRole, msg_type: MessageType, payload: Dict):
        """ส่งข้อความไปยัง Agent อื่น"""
        message = AgentMessage.create(
            from_agent=self.role,
            to_agent=target,
            msg_type=msg_type,
            payload=payload
        )
        await self.orchestrator.bus.publish(message)
    
    async def broadcast(self, event_name: str, data: Dict = None):
        """ประกาศไปยังทุก Agent"""
        await self.orchestrator.broadcast_event(self.role, event_name, data)


# 🧪 Test Functions
async def test_orchestrator():
    """ทดสอบ Orchestrator"""
    print("\n" + "=" * 60)
    print("🧪 Testing SwarmOrchestrator")
    print("=" * 60)
    
    orch = get_orchestrator()
    
    # Create test agents
    class TestAgent(BaseAgent):
        async def handle_command(self, command, data):
            print(f"  📥 {self.role.value} executing: {command}")
            if command == "search":
                await self.send_to(AgentRole.JOURNEY_ARCHITECT, MessageType.RESPONSE, 
                                 {"results": ["video1", "video2"]})
    
    # Register agents
    search_agent = TestAgent(AgentRole.SEARCH_SPECIALIST)
    journey_agent = TestAgent(AgentRole.JOURNEY_ARCHITECT)
    front_desk = TestAgent(AgentRole.FRONT_DESK)
    
    # Test 1: Direct message
    print("\n📋 Test 1: Direct Message")
    await orch.send_command(
        AgentRole.FRONT_DESK,
        AgentRole.SEARCH_SPECIALIST,
        "search",
        {"query": "การให้อภัย"}
    )
    
    await asyncio.sleep(0.5)
    
    # Test 2: Broadcast
    print("\n📋 Test 2: Broadcast Event")
    await orch.broadcast_event(AgentRole.SENTINEL, "user_online", {"user_id": "123"})
    
    await asyncio.sleep(0.5)
    
    # Test 3: Workflow
    print("\n📋 Test 3: Execute Workflow")
    result = await orch.execute_workflow(
        "user_message",
        {"user_id": "test123", "message": "สวัสดี"}
    )
    print(f"  Workflow result: {result}")
    
    print("\n✅ Orchestrator tests complete!")
    
    # Show agent status
    print("\n📊 Agent Status:")
    for role, status in orch.get_agent_status().items():
        icon = "✅" if status == "registered" else "❌"
        print(f"  {icon} {role}: {status}")


if __name__ == "__main__":
    print("=" * 60)
    print("🎯 SWARM ORCHESTRATOR & COMMUNICATION PROTOCOL")
    print("=" * 60)
    asyncio.run(test_orchestrator())
