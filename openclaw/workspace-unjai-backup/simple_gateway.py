"""
Simplified LINE Gateway - Direct Pinecone Connection
ไม่ใช้ Swarm 15 Agents - เชื่อมต่อตรง LINE ↔ Pinecone
"""
import os
import sys

# Load .env file
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

import json
import hmac
import hashlib
import base64
from typing import Dict, Optional
from datetime import datetime
import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FlexSendMessage, VideoSendMessage
)
import httpx

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SimpleGateway")


class SimplePineconeConnector:
    """
    🔍 Simple Pinecone Connector - ไม่ผ่าน Swarm
    เชื่อมต่อตรงกับ Pinecone API
    """
    
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_host = os.getenv("PINECONE_INDEX_HOST")
        self.namespace = os.getenv("PINECONE_NAMESPACE", "highlights")
        self.base_url = os.getenv("BASE_URL", "https://nongaunjai.febradio.org")
        
        if not self.api_key or not self.index_host:
            logger.warning("⚠️ Pinecone not configured properly")
        else:
            logger.info(f"✅ Pinecone connected: {self.index_host}")
            logger.info(f"   Base URL: {self.base_url}")
    
    async def search(self, query: str, top_k: int = 3) -> list:
        """
        ค้นหา video ใน Pinecone
        """
        if not self.api_key or not self.index_host:
            logger.error("❌ Pinecone not configured")
            return []
        
        try:
            # 1. Generate embedding using OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                logger.error("❌ OPENAI_API_KEY not set")
                return []
            
            async with httpx.AsyncClient() as client:
                # Get embedding
                embed_response = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    json={
                        "input": query,
                        "model": "text-embedding-3-small",
                        "dimensions": 384
                    },
                    timeout=30.0
                )
                embed_response.raise_for_status()
                embedding = embed_response.json()["data"][0]["embedding"]
                
                # Search Pinecone
                search_response = await client.post(
                    f"{self.index_host}/query",
                    headers={
                        "Api-Key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "namespace": self.namespace,
                        "vector": embedding,
                        "topK": top_k,
                        "includeMetadata": True,
                        "includeValues": False
                    },
                    timeout=30.0
                )
                search_response.raise_for_status()
                
                data = search_response.json()
                matches = data.get("matches", [])
                
                results = []
                for match in matches:
                    score = match.get("score", 0)
                    metadata = match.get("metadata", {})
                    
                    if score >= 0.70 and metadata.get("clip_url"):
                        raw_url = metadata.get("clip_url", "")
                        # Add base URL if needed
                        full_url = f"{self.base_url}{raw_url}" if raw_url.startswith("/") else raw_url
                        
                        results.append({
                            "id": match["id"],
                            "clip_url": full_url,
                            "video_url": metadata.get("video_url", ""),
                            "transcript": metadata.get("transcript", "")[:200],
                            "reason": metadata.get("reason", "")[:100],
                            "score": score,
                            "title": metadata.get("title", "คลิปหนุนใจ")
                        })
                
                logger.info(f"✅ Found {len(results)} videos for: {query[:30]}...")
                return results
                
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            import traceback
            traceback.print_exc()
            return []


class SimpleLINEGateway:
    """
    📱 Simple LINE Gateway - ไม่ผ่าน Swarm
    """
    
    def __init__(self):
        self.channel_secret = os.getenv("LINE_CHANNEL_SECRET")
        self.channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self.pinecone = SimplePineconeConnector()
        
        if self.channel_access_token:
            self.line_bot_api = LineBotApi(self.channel_access_token)
        else:
            logger.warning("⚠️ LINE credentials not set")
            self.line_bot_api = None
        
        logger.info("✅ Simple LINE Gateway initialized (No Swarm)")
    
    def verify_signature(self, body: str, signature: str) -> bool:
        """Verify LINE webhook signature"""
        try:
            hash_val = hmac.new(
                self.channel_secret.encode('utf-8'),
                body.encode('utf-8'),
                hashlib.sha256
            ).digest()
            expected = base64.b64encode(hash_val).decode('utf-8')
            return hmac.compare_digest(expected, signature)
        except Exception as e:
            logger.error(f"Signature error: {e}")
            return False
    
    async def handle_message(self, user_id: str, message: str) -> Dict:
        """
        จัดการข้อความ - ตรงไปตรงมา
        """
        logger.info(f"📩 From {user_id}: {message[:50]}...")
        
        # 1. ค้นหาใน Pinecone
        videos = await self.pinecone.search(message)
        
        if not videos:
            # ไม่เจอ video - ตอบข้อความธรรมดา
            return {
                "type": "text",
                "content": f"สวัสดีค่ะคุณพี่! อุ่นใจได้รับข้อความ: \"{message[:30]}...\" แต่ยังไม่เจอคลิปที่ตรงกับคำถามนี้ค่ะ 💕"
            }
        
        # 2. สร้าง Flex Message สำหรับ video
        video = videos[0]
        
        flex_content = {
            "type": "bubble",
            "hero": {
                "type": "video",
                "url": video["clip_url"],
                "previewUrl": f"https://img.youtube.com/vi/{self._extract_yt_id(video['video_url'])}/0.jpg" if video['video_url'] else video["clip_url"]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": video["title"],
                        "weight": "bold",
                        "size": "lg"
                    },
                    {
                        "type": "text",
                        "text": video["transcript"],
                        "size": "sm",
                        "color": "#666666",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": f"ความตรงกัน: {video['score']:.0%}",
                        "size": "xs",
                        "color": "#999999",
                        "margin": "md"
                    }
                ]
            }
        }
        
        return {
            "type": "flex",
            "flex_content": flex_content,
            "alt_text": f"🎬 {video['title']}"
        }
    
    def _extract_yt_id(self, url: str) -> str:
        """Extract YouTube video ID"""
        if not url:
            return ""
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        if "/" in url:
            return url.split("/")[-1]
        return url
    
    async def send_response(self, reply_token: str, response: Dict):
        """ส่งข้อความตอบกลับ"""
        try:
            msg_type = response.get("type", "text")
            
            if msg_type == "text":
                message = TextSendMessage(text=response["content"])
            elif msg_type == "flex":
                message = FlexSendMessage(
                    alt_text=response.get("alt_text", "Message from Nong Unjai"),
                    contents=response["flex_content"]
                )
            else:
                message = TextSendMessage(text="ขออภัยค่ะ มีข้อผิดพลาด")
            
            if self.line_bot_api and reply_token:
                self.line_bot_api.reply_message(reply_token, message)
                logger.info(f"✅ Response sent")
            
        except Exception as e:
            logger.error(f"❌ Send error: {e}")


# Create FastAPI app
gateway = SimpleLINEGateway()
app = FastAPI(title="Nong Unjai Simple Gateway")

@app.post("/webhook/line")
async def webhook(request: Request):
    """LINE webhook endpoint"""
    body = await request.body()
    body_text = body.decode('utf-8')
    signature = request.headers.get('X-Line-Signature', '')
    
    # Verify signature
    if not gateway.verify_signature(body_text, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    try:
        data = json.loads(body_text)
        events = data.get("events", [])
        
        for event in events:
            if event.get("type") == "message":
                msg = event.get("message", {})
                if msg.get("type") == "text":
                    user_id = event.get("source", {}).get("userId")
                    text = msg.get("text", "")
                    reply_token = event.get("replyToken")
                    
                    # Process message
                    response = await gateway.handle_message(user_id, text)
                    await gateway.send_response(reply_token, response)
        
        return JSONResponse(content={"status": "ok"})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse(content={"status": "error"}, status_code=500)

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "mode": "simple (no swarm)",
        "pinecone": "connected" if gateway.pinecone.api_key else "not configured",
        "line": "connected" if gateway.line_bot_api else "not configured",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting Simple Gateway on {host}:{port}")
    logger.info("⚠️  Swarm 15 Agents: DISABLED")
    logger.info("✅ Direct LINE ↔ Pinecone connection")
    
    uvicorn.run(app, host=host, port=port)
