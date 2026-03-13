"""
🎯 Nong Unjai - Orchestrator/Gateway Coordination Protocol
ระบบประสานงานและโปรโตคอลการสื่อสารระหว่าง Gateway ↔ Orchestrator ↔ Agents
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
logger = logging.getLogger("OrchestratorGateway")


class CoordinationStatus(Enum):
    """สถานะการประสานงาน"""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING_AGENT = "waiting_agent"
    COMPLETED = "completed"
    ERROR = "error"


class AgentTaskType(Enum):
    """ประเภทงานที่มอบหมายให้ Agents"""
    SEARCH = "search"
    ANALYZE = "analyze"
    DECIDE = "decide"
    RESPOND = "respond"
    SAFETY_CHECK = "safety_check"
    DELIVER = "deliver"


@dataclass
class TaskAllocation:
    """การมอบหมายงานให้ Agent"""
    task_id: str
    task_type: AgentTaskType
    agent_role: str
    payload: Dict[str, Any]
    status: CoordinationStatus = CoordinationStatus.IDLE
    result: Optional[Dict] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "agent_role": self.agent_role,
            "payload": self.payload,
            "status": self.status.value,
            "result": self.result,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message
        }


@dataclass
class CoordinationSession:
    """เซสชั่นการประสานงาน"""
    session_id: str
    user_id: str
    message: str
    status: CoordinationStatus
    tasks: List[TaskAllocation] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    final_response: Optional[Dict] = None
    
    def add_task(self, task: TaskAllocation):
        """เพิ่มงานใหม่"""
        self.tasks.append(task)
        self.updated_at = datetime.now()
    
    def update_task_status(self, task_id: str, status: CoordinationStatus, 
                          result: Optional[Dict] = None, error: Optional[str] = None):
        """อัปเดตสถานะงาน"""
        for task in self.tasks:
            if task.task_id == task_id:
                task.status = status
                if status == CoordinationStatus.PROCESSING and not task.started_at:
                    task.started_at = datetime.now()
                if status in [CoordinationStatus.COMPLETED, CoordinationStatus.ERROR]:
                    task.completed_at = datetime.now()
                task.result = result
                task.error_message = error
                break
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "message": self.message,
            "status": self.status.value,
            "tasks": [t.to_dict() for t in self.tasks],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "final_response": self.final_response
        }


class AgentRegistry:
    """
    📝 Agent Registry - ลงทะเบียนและจัดการ Agents
    """
    
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.capabilities: Dict[str, List[str]] = {}
        logger.info("📝 AgentRegistry initialized")
    
    def register(self, role: str, handler: Callable, capabilities: List[str] = None):
        """ลงทะเบียน Agent"""
        self.agents[role] = {
            "handler": handler,
            "status": "active",
            "registered_at": datetime.now(),
            "last_active": datetime.now()
        }
        self.capabilities[role] = capabilities or []
        logger.info(f"✅ Agent registered: {role} (capabilities: {capabilities})")
    
    def get_agent(self, role: str) -> Optional[Callable]:
        """ดึง handler ของ Agent"""
        agent = self.agents.get(role)
        if agent:
            agent["last_active"] = datetime.now()
            return agent["handler"]
        return None
    
    def find_agents_by_capability(self, capability: str) -> List[str]:
        """หา Agents ตามความสามารถ"""
        return [role for role, caps in self.capabilities.items() if capability in caps]
    
    def get_all_active(self) -> List[str]:
        """ดึงรายชื่อ Agents ที่ active"""
        return [role for role, info in self.agents.items() if info["status"] == "active"]


class GatewayOrchestratorCoordinator:
    """
    🎯 Gateway-Orchestrator Coordinator
    ประสานงานระหว่าง Gateway และ Orchestrator
    """
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.sessions: Dict[str, CoordinationSession] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        logger.info("🎯 GatewayOrchestratorCoordinator initialized")
    
    async def start(self):
        """เริ่มระบบประสานงาน"""
        self.running = True
        asyncio.create_task(self._process_queue())
        logger.info("🚀 Coordinator started")
    
    async def stop(self):
        """หยุดระบบ"""
        self.running = False
        logger.info("🛑 Coordinator stopped")
    
    async def _process_queue(self):
        """ประมวลผลคิวข้อความ"""
        while self.running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self._handle_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Queue processing error: {e}")
    
    async def _handle_message(self, message: Dict):
        """จัดการข้อความในคิว"""
        msg_type = message.get("type")
        
        if msg_type == "task_request":
            await self._assign_task(message)
        elif msg_type == "task_complete":
            await self._handle_task_completion(message)
        elif msg_type == "agent_status":
            await self._update_agent_status(message)
    
    async def create_session(self, user_id: str, message: str) -> str:
        """สร้างเซสชั่นการประสานงานใหม่"""
        import uuid
        session_id = str(uuid.uuid4())[:12]
        
        session = CoordinationSession(
            session_id=session_id,
            user_id=user_id,
            message=message,
            status=CoordinationStatus.IDLE
        )
        self.sessions[session_id] = session
        logger.info(f"📋 Session created: {session_id} for user {user_id}")
        return session_id
    
    async def coordinate_request(self, user_id: str, message: str) -> Dict:
        """
        ประสานงานจัดการคำขอ - Workflow หลัก
        """
        # 1. สร้างเซสชั่น
        session_id = await self.create_session(user_id, message)
        session = self.sessions[session_id]
        session.status = CoordinationStatus.PROCESSING
        
        logger.info(f"🎯 Starting coordination for session {session_id}")
        
        try:
            # 2. ส่งงานให้ Search Specialist
            search_task = TaskAllocation(
                task_id=f"{session_id}_search",
                task_type=AgentTaskType.SEARCH,
                agent_role="search_specialist",
                payload={"query": message, "user_id": user_id}
            )
            session.add_task(search_task)
            search_result = await self._execute_task(search_task)
            
            # 3. ส่งงานให้ Journey Architect ตัดสินใจ
            decision_task = TaskAllocation(
                task_id=f"{session_id}_decide",
                task_type=AgentTaskType.DECIDE,
                agent_role="journey_architect",
                payload={
                    "message": message,
                    "search_results": search_result,
                    "user_id": user_id
                }
            )
            session.add_task(decision_task)
            decision_result = await self._execute_task(decision_task)
            
            # 4. ส่งงานให้ Front-Desk สร้าง response
            respond_task = TaskAllocation(
                task_id=f"{session_id}_respond",
                task_type=AgentTaskType.RESPOND,
                agent_role="front_desk",
                payload={
                    "message": message,
                    "decision": decision_result,
                    "search_results": search_result,
                    "user_id": user_id
                }
            )
            session.add_task(respond_task)
            response = await self._execute_task(respond_task)
            
            # 5. ส่งงานให้ Media Delivery (ถ้ามี video metadata จาก Front-Desk)
            if response.get("type") == "video":
                logger.info(f"📦 Passing video metadata to Media Delivery Agent for Flex Message building")
                delivery_task = TaskAllocation(
                    task_id=f"{session_id}_deliver",
                    task_type=AgentTaskType.DELIVER,
                    agent_role="media_delivery",
                    payload={"response": response}
                )
                session.add_task(delivery_task)
                delivery_result = await self._execute_task(delivery_task)
                
                # Use the built flex message from Media Delivery
                if delivery_result and delivery_result.get("status") == "delivered":
                    response = {
                        "type": "flex",
                        "flex_content": delivery_result.get("content"),
                        "alt_text": delivery_result.get("alt_text", "🎬 คลิปหนุนใจ"),
                        "metadata": delivery_result.get("metadata", {})
                    }
                    logger.info(f"✅ Media Delivery Agent built Flex Message successfully")
            
            # 6. เสร็จสิ้น
            session.status = CoordinationStatus.COMPLETED
            session.final_response = response
            
            logger.info(f"✅ Coordination completed for session {session_id}")
            return response
            
        except Exception as e:
            session.status = CoordinationStatus.ERROR
            logger.error(f"❌ Coordination failed for session {session_id}: {e}")
            return {
                "type": "text",
                "content": f"ขออภัยค่ะคุณพี่ อุ่นใจมีปัญหาในการประมวลผล กรุณาลองใหม่อีกครั้งนะคะ 🙏"
            }
    
    async def _execute_task(self, task: TaskAllocation) -> Dict:
        """รันงานผ่าน Agent"""
        handler = self.registry.get_agent(task.agent_role)
        if not handler:
            raise ValueError(f"Agent {task.agent_role} not found")
        
        task.status = CoordinationStatus.PROCESSING
        task.started_at = datetime.now()
        
        logger.info(f"🔄 Executing task {task.task_id} with {task.agent_role}")
        
        try:
            result = await handler(task.payload)
            task.status = CoordinationStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            logger.info(f"✅ Task {task.task_id} completed")
            return result
            
        except Exception as e:
            task.status = CoordinationStatus.ERROR
            task.error_message = str(e)
            task.completed_at = datetime.now()
            logger.error(f"❌ Task {task.task_id} failed: {e}")
            raise
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """ดูสถานะเซสชั่น"""
        session = self.sessions.get(session_id)
        if session:
            return session.to_dict()
        return None
    
    def get_all_sessions(self) -> List[Dict]:
        """ดูสถานะทุกเซสชั่น"""
        return [s.to_dict() for s in self.sessions.values()]


# Singleton
coordinator_instance: Optional[GatewayOrchestratorCoordinator] = None

def get_coordinator() -> GatewayOrchestratorCoordinator:
    """Get coordinator singleton"""
    global coordinator_instance
    if coordinator_instance is None:
        coordinator_instance = GatewayOrchestratorCoordinator()
    return coordinator_instance


if __name__ == "__main__":
    # Test
    async def test():
        coord = get_coordinator()
        await coord.start()
        
        # Register dummy agents
        async def dummy_handler(payload):
            return {"result": "ok", "payload": payload}
        
        coord.registry.register("search_specialist", dummy_handler, ["search"])
        coord.registry.register("journey_architect", dummy_handler, ["decide"])
        coord.registry.register("front_desk", dummy_handler, ["respond"])
        
        # Test coordination
        result = await coord.coordinate_request("user_001", "สวัสดีค่ะ")
        print(f"Result: {result}")
        
        await coord.stop()
    
    asyncio.run(test())
