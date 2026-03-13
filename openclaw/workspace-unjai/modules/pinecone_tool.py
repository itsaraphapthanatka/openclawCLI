"""
Search Specialist Tool for OpenClaw
Enables automatic Pinecone vector search
"""
import os
import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional
from openai import OpenAI

class SearchSpecialist:
    """
    Agent: Search Specialist
    Role: นักสืบค้นหาความหมาย (Parallel Retriever)
    Task: Hybrid Search (Text + Video from Pinecone)
    """
    
    def __init__(self):
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_host = os.getenv("PINECONE_HOST", 
            "https://aunjai-knowledge-3ygam8j.svc.aped-4627-b74a.pinecone.io")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "aunjai-knowledge")
        self.namespace = os.getenv("PINECONE_NAMESPACE", "highlights")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("BASE_URL", "https://nongaunjai.febradio.org")
        
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI text-embedding-3-small (384 dims)"""
        try:
            client = OpenAI(api_key=self.openai_api_key)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                dimensions=384  # Match Pinecone index
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def _query_pinecone(self, vector: List[float], top_k: int = 5, 
                        min_score: float = 0.70) -> List[Dict]:
        """Query Pinecone vector database"""
        url = f"{self.pinecone_host}/query"
        
        headers = {
            "Api-Key": self.pinecone_api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "namespace": self.namespace,
            "vector": vector,
            "topK": top_k,
            "includeMetadata": True,
            "includeValues": False
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            # Filter by min_score and ensure clip_url exists
            matches = []
            for match in result.get("matches", []):
                score = match.get("score", 0)
                metadata = match.get("metadata", {})
                
                if score >= min_score and metadata.get("clip_url"):
                    # Add full URL
                    clip_url = metadata["clip_url"]
                    if not clip_url.startswith("http"):
                        metadata["clip_url"] = f"{self.base_url}{clip_url}"
                    
                    matches.append({
                        "id": match["id"],
                        "score": score,
                        "metadata": metadata
                    })
            
            return matches
            
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            return []
        except Exception as e:
            print(f"Error querying Pinecone: {e}")
            return []
    
    def search(self, query: str, top_k: int = 5, 
               min_score: float = 0.70) -> Dict:
        """
        Hybrid Parallel Search (Text + Video)
        
        Args:
            query: คำค้นหาจากผู้ใช้ (เช่น "การให้อภัย", "บาป ความตาย")
            top_k: จำนวนผลลัพธ์สูงสุด
            min_score: คะแนนขั้นต่ำ (default 0.70)
        
        Returns:
            Dictionary มี video_results และ text_results
        """
        print(f"🔍 Search Specialist: กำลังค้นหา '{query}'...")
        
        # 1. Generate embedding
        vector = self._generate_embedding(query)
        if not vector:
            return {"video_results": [], "text_results": []}
        
        # 2. Query Pinecone
        video_results = self._query_pinecone(vector, top_k, min_score)
        
        # 3. Return results (text_results จาก MEMORY.md ทำแยก)
        return {
            "video_results": video_results,
            "text_results": [],  # ค้นหาจาก MEMORY.md แยก
            "query": query,
            "total_found": len(video_results)
        }
    
    def search_by_id(self, clip_id: str) -> Optional[Dict]:
        """Fetch specific clip by ID"""
        url = f"{self.pinecone_host}/vectors/fetch"
        
        headers = {
            "Api-Key": self.pinecone_api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "namespace": self.namespace,
            "ids": [clip_id]
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            vectors = result.get("vectors", {})
            if clip_id in vectors:
                metadata = vectors[clip_id].get("metadata", {})
                # Add full URL
                clip_url = metadata.get("clip_url", "")
                if clip_url and not clip_url.startswith("http"):
                    metadata["clip_url"] = f"{self.base_url}{clip_url}"
                return metadata
            
            return None
            
        except Exception as e:
            print(f"Error fetching by ID: {e}")
            return None


# Singleton instance
_search_specialist = None

def get_search_specialist() -> SearchSpecialist:
    """Get or create Search Specialist instance"""
    global _search_specialist
    if _search_specialist is None:
        _search_specialist = SearchSpecialist()
    return _search_specialist


# Example usage
if __name__ == "__main__":
    # Test
    specialist = get_search_specialist()
    
    # Test search
    result = specialist.search("บาป ความตาย", top_k=3)
    print(f"Found {result['total_found']} videos")
    for video in result["video_results"]:
        print(f"  - {video['metadata'].get('title', 'Untitled')} (score: {video['score']:.2f})")
    
    # Test fetch by ID
    clip = specialist.search_by_id("16f641bdc0cffbaf34ca29ee051c13cb")
    if clip:
        print(f"\nClip found: {clip.get('clip_url')}")
