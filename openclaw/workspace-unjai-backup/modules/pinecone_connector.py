"""
Pinecone + LINE Integration - Production Ready Connector
เชื่อมต่อจริงกับ Pinecone API
"""

import os
import json
import ssl
import urllib.request
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PineconeVideoResult:
    """Video result from Pinecone search"""
    id: str
    score: float
    clip_url: str
    video_url: str
    start_time: int
    end_time: int
    transcript: str
    reason: str
    type: str = "highlight"


class PineconeConnector:
    """
    🔍 Production-ready Pinecone Connector
    ใช้ urllib แทน httpx เพื่อไม่ต้องติดตั้ง library เพิ่ม
    """
    
    # 🎯 Base URL สำหรับ clip videos
    BASE_URL = "https://nongaunjai.febradio.org"
    
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_host = os.getenv("PINECONE_INDEX_HOST")
        self.namespace = os.getenv("PINECONE_NAMESPACE", "highlights")
        
        # Load BASE_URL from environment (override class default if set)
        env_base_url = os.getenv("BASE_URL")
        if env_base_url:
            self.BASE_URL = env_base_url
        
        # SSL context (disable verification for some environments)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        if not self.api_key or not self.index_host:
            raise ValueError("PINECONE_API_KEY and PINECONE_INDEX_HOST must be set")
        
        logger.info(f"🔌 PineconeConnector initialized")
        logger.info(f"   Host: {self.index_host}")
        logger.info(f"   Namespace: {self.namespace}")
        logger.info(f"   Base URL: {self.BASE_URL}")
        logger.info(f"   (from env: {env_base_url is not None})")
    
    def _make_request(self, endpoint: str, payload: Dict) -> Dict:
        """Make HTTP request to Pinecone"""
        url = f"{self.index_host}/{endpoint}"
        headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        logger.info(f"🌐 Making request to: {url}")
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                logger.info(f"✅ Request successful")
                return result
                
        except urllib.error.HTTPError as e:
            logger.error(f"❌ HTTP Error {e.code}: {e.reason}")
            try:
                error_body = e.read().decode('utf-8')
                logger.error(f"   Response: {error_body}")
            except:
                pass
            raise
        except urllib.error.URLError as e:
            logger.error(f"❌ URL Error: {e.reason}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error: {type(e).__name__}: {e}")
            raise
    
    def search_by_vector(self, 
                        vector: List[float],
                        top_k: int = 3,
                        min_score: float = 0.70,
                        filter: Optional[Dict[str, Any]] = None) -> List[PineconeVideoResult]:
        """
        🔍 Search videos by vector embedding
        
        Args:
            vector: Embedding vector (384 dimensions)
            top_k: Number of results to return
            min_score: Minimum similarity score
            filter: Metadata filter (Pinecone query filter syntax)
            
        Returns:
            List of PineconeVideoResult with clip_url, transcript, etc.
        """
        try:
            payload = {
                "namespace": self.namespace,
                "vector": vector,
                "topK": top_k,
                "includeMetadata": True
            }
            
            if filter:
                payload["filter"] = filter
                logger.info(f"📊 Using filter: {json.dumps(filter)}")
            
            logger.info(f"🔍 Searching Pinecone (top_k={top_k}, min_score={min_score})")
            data = self._make_request("query", payload)
            
            matches = data.get("matches", [])
            results = []
            
            for match in matches:
                score = match.get("score", 0)
                metadata = match.get("metadata", {})
                
                # Filter by min_score and ensure clip_url exists
                if score >= min_score and metadata.get("clip_url"):
                    # 🎯 เติม Base URL นำหน้า clip_url
                    raw_clip_url = metadata.get("clip_url", "")
                    full_clip_url = f"{self.BASE_URL}{raw_clip_url}" if raw_clip_url.startswith("/") else raw_clip_url
                    
                    results.append(PineconeVideoResult(
                        id=match["id"],
                        score=score,
                        clip_url=full_clip_url,
                        video_url=metadata.get("video_url", ""),
                        start_time=metadata.get("start_time", 0),
                        end_time=metadata.get("end_time", 0),
                        transcript=metadata.get("transcript", ""),
                        reason=metadata.get("reason", ""),
                        type=metadata.get("type", "highlight")
                    ))
            
            logger.info(f"✅ Found {len(results)} valid video highlights")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching Pinecone: {e}")
            return []
    
    def search_by_text(self, 
                      text: str,
                      openai_api_key: Optional[str] = None,
                      top_k: int = 3,
                      min_score: float = 0.70,
                      filter: Optional[Dict[str, Any]] = None) -> List[PineconeVideoResult]:
        """
        🔍 Search videos by text (auto-generates embedding)
        
        Args:
            text: Search query text (Thai or English)
            openai_api_key: OpenAI API key for embeddings
            top_k: Number of results
            min_score: Minimum similarity score
            filter: Metadata filter
            
        Returns:
            List of PineconeVideoResult
        """
        # Generate embedding using OpenAI
        vector = self._generate_embedding(text, openai_api_key)
        
        if not vector:
            logger.warning("⚠️ Could not generate embedding, returning empty results")
            return []
        
        return self.search_by_vector(vector, top_k, min_score, filter)
    
    def _generate_embedding(self, 
                           text: str,
                           api_key: Optional[str] = None) -> Optional[List[float]]:
        """
        Generate embedding using OpenAI API
        Note: Pinecone index uses 384 dimensions
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            logger.error("❌ OPENAI_API_KEY not set")
            return None
        
        try:
            url = "https://api.openai.com/v1/embeddings"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "text-embedding-3-small",
                "input": text[:8000],  # Limit text length
                "dimensions": 384  # 🔧 กำหนดให้ตรงกับ Pinecone index
            }
            
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                embedding = data["data"][0]["embedding"]
                logger.info(f"✅ Generated embedding ({len(embedding)} dimensions)")
                return embedding
                
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            return None
    
    def get_sample_records(self, count: int = 5) -> List[PineconeVideoResult]:
        """Get sample records (using zero vector - returns random-ish results)"""
        zero_vector = [0.0] * 384
        return self.search_by_vector(zero_vector, top_k=count, min_score=0.0)


# 🚀 Singleton instance for easy import
pinecone_connector: Optional[PineconeConnector] = None

def get_connector() -> PineconeConnector:
    """Get or create Pinecone connector singleton"""
    global pinecone_connector
    if pinecone_connector is None:
        pinecone_connector = PineconeConnector()
    return pinecone_connector


# 🧪 Test function
if __name__ == "__main__":
    print("=" * 60)
    print("🔍 Testing Pinecone + LINE Integration")
    print("=" * 60)
    
    # Initialize connector
    connector = get_connector()
    
    # Test 1: Get sample records
    print("\n📹 Test 1: Get sample records")
    samples = connector.get_sample_records(3)
    
    if samples:
        print(f"✅ Found {len(samples)} sample videos:")
        for i, video in enumerate(samples, 1):
            print(f"\n  {i}. Score: {video.score:.3f}")
            print(f"     Clip: {video.clip_url}")
            print(f"     Reason: {video.reason[:50]}...")
    else:
        print("⚠️ No sample records found")
    
    # Test 2: Search with OpenAI embedding (if API key available)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("\n🔎 Test 2: Search with Thai text")
        print("   Query: 'การให้อภัย'")
        
        results = connector.search_by_text(
            text="การให้อภัย",
            openai_api_key=openai_key,
            top_k=3,
            min_score=0.70
        )
        
        if results:
            print(f"✅ Found {len(results)} matching videos:")
            for video in results:
                print(f"\n   🎬 Score: {video.score:.3f}")
                print(f"      Clip: {video.clip_url}")
                print(f"      Transcript: {video.transcript[:80]}...")
        else:
            print("⚠️ No matching videos found")
    else:
        print("\n⏭️ Test 2 skipped (OPENAI_API_KEY not set)")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete")
    print("=" * 60)
