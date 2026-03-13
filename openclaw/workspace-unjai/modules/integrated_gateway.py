"""
LINE Gateway + Swarm Integration
เชื่อมต่อ LINE Gateway เข้ากับ Swarm Orchestrator อย่างถูกต้อง
"""
import os
import sys
import asyncio
from typing import Dict
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LINEGatewaySwarm")

# Import required modules
sys.path.insert(0, '/home/node/.openclaw/workspace-unjai/modules')

from module_4_line_gateway import (
    LineGateway, ParsedMessage, UserSession, 
    create_app, MessageType
)
from line_orchestrator import LineOrchestrator


class IntegratedGateway:
    """
    Gateway ที่เชื่อมต่อ LINE + Pinecone + Swarm อย่างสมบูรณ์
    """
    
    def __init__(self):
        self.line_gateway = LineGateway()
        self.orchestrator = LineOrchestrator()
        
        # Setup message handler
        self.line_gateway.set_message_handler(self._handle_message)
        
        logger.info("✅ Integrated Gateway initialized")
    
    async def _handle_message(self, parsed: ParsedMessage, session: UserSession) -> Dict:
        """
        จัดการข้อความจากผู้ใช้ - เชื่อมต่อกับ Pinecone/Swarm
        """
        try:
            logger.info(f"📩 Handling message: {parsed.content[:50]}...")
            
            # ใช้ LineOrchestrator จัดการข้อความ
            response = await self.orchestrator.handle_message(parsed, session)
            
            logger.info(f"✅ Response ready: {response.get('type', 'unknown')}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
            import traceback
            traceback.print_exc()
            
            # Return safe fallback
            return {
                "type": "text",
                "content": f"ขออภัยค่ะคุณพี่ อุ่นใจมีปัญหาเล็กน้อย ({str(e)[:50]}) กรุณาลองใหม่อีกครั้งนะคะ 🙏"
            }
    
    def get_app(self):
        """Get FastAPI app with integrated handlers"""
        return create_app(self.line_gateway)


# Singleton
gateway_instance = None

def get_integrated_gateway():
    """Get or create integrated gateway"""
    global gateway_instance
    if gateway_instance is None:
        gateway_instance = IntegratedGateway()
    return gateway_instance


if __name__ == "__main__":
    import uvicorn
    
    # Initialize
    gateway = get_integrated_gateway()
    app = gateway.get_app()
    
    # Get config
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"🚀 Starting Integrated LINE Gateway on {host}:{port}")
    logger.info(f"   Base URL: {os.getenv('BASE_URL', 'https://nongaunjai.febradio.org')}")
    logger.info(f"   Pinecone: {os.getenv('PINECONE_INDEX_HOST', 'NOT SET')}")
    
    uvicorn.run(app, host=host, port=port)
