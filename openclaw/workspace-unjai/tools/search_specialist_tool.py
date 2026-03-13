#!/usr/bin/env python3
"""
🔍 Search Specialist Auto-Tool v2.0
Full Hybrid Search Implementation - ตาม AGENTS.md อย่างเคร่งครัด

Role: นักสืบค้นหาความหมาย (Parallel Retriever)
Task: รันระบบค้นหาแบบคู่ขนาน (Hybrid Search) เสมอ
กฎเหล็ก: หากพบวิดีโอที่มี Similarity Score > 0.80 ห้ามทิ้ง! 
         ต้องส่ง Metadata (URL, Quiz, Reason) แนบไปกับชุดคำตอบเสมอ
"""
import os
import sys
import json
import ssl
import urllib.request
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment
env_path = Path(__file__).parent.parent / "docker" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val


class SearchSpecialistTool:
    """
    🔍 Search Specialist Auto-Tool v2.0
    
    ค้นหาแบบ Hybrid Parallel Search (Text + Video) อัตโนมัติ
    ตามกฎเหล็กของ AGENTS.md
    """
    
    # กฎเหล็ก: Threshold สำหรับ video ที่ต้องส่งต่อเสมอ
    IRON_RULE_THRESHOLD = 0.80
    
    def __init__(self):
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_index_host = os.getenv("PINECONE_INDEX_HOST")
        self.pinecone_namespace = os.getenv("PINECONE_NAMESPACE", "highlights")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("BASE_URL", "https://nongaunjai.febradio.org")
        self.memory_file = Path(__file__).parent.parent / "MEMORY.md"
        
        # SSL context
        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE
    
    def generate_embedding(self, text: str) -> List[float]:
        """สร้าง embedding vector จากข้อความ"""
        try:
            req = urllib.request.Request(
                "https://api.openai.com/v1/embeddings",
                data=json.dumps({
                    "model": "text-embedding-3-small",
                    "input": text[:8000],
                    "dimensions": 384
                }).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                method='POST'
            )
            
            with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data["data"][0]["embedding"]
                
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            return [0.0] * 384
    
    def search_memory_md(self, query: str) -> List[Dict]:
        """
        🔍 ค้นหา Text จาก MEMORY.md (ฐานคำตอบหลัก)
        
        ค้นหาแบบ keyword matching + semantic similarity ง่ายๆ
        """
        results = []
        
        try:
            if not self.memory_file.exists():
                return results
            
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into sections (topics)
            sections = re.split(r'\n##+\s+', content)
            
            # Keywords from query
            query_keywords = set(query.lower().split())
            
            for section in sections:
                if not section.strip():
                    continue
                
                # Simple keyword matching score
                section_lower = section.lower()
                match_count = sum(1 for kw in query_keywords if kw in section_lower)
                
                if match_count > 0:
                    # Calculate simple relevance score
                    score = min(match_count / len(query_keywords), 1.0)
                    
                    # Extract title (first line)
                    lines = section.strip().split('\n')
                    title = lines[0][:100] if lines else "Untitled"
                    
                    # Extract content preview
                    preview = section[:500].replace('\n', ' ')
                    
                    results.append({
                        "type": "text",
                        "source": "MEMORY.md",
                        "title": title,
                        "content": preview,
                        "score": score,
                        "match_count": match_count
                    })
            
            # Sort by score
            results.sort(key=lambda x: x["score"], reverse=True)
            
        except Exception as e:
            print(f"⚠️  MEMORY.md search error: {e}")
        
        return results[:5]  # Return top 5
    
    def search_pinecone(self, 
                       embedding: List[float],
                       top_k: int = 5,
                       min_score: float = 0.05) -> List[Dict]:
        """
        🔍 ค้นหา Vector จาก Pinecone (Namespace: highlights)
        
        เพื่อหาคลิปที่เกี่ยวข้อง
        """
        try:
            req = urllib.request.Request(
                f"{self.pinecone_index_host}/query",
                data=json.dumps({
                    "namespace": self.pinecone_namespace,
                    "vector": embedding,
                    "topK": top_k,
                    "includeMetadata": True,
                    "includeValues": False
                }).encode('utf-8'),
                headers={
                    "Api-Key": self.pinecone_api_key,
                    "Content-Type": "application/json"
                },
                method='POST'
            )
            
            with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                matches = data.get("matches", [])
                
                results = []
                for match in matches:
                    score = match.get("score", 0)
                    
                    # เก็บทุกผลลัพธ์ที่มี score >= min_score
                    # กฎเหล็ก: ถ้า score > 0.80 จะถูก mark เป็น high_priority
                    if score < min_score:
                        continue
                    
                    metadata = match.get("metadata", {})
                    raw_clip_url = metadata.get("clip_url", "")
                    
                    # Add base URL if needed
                    if raw_clip_url.startswith("/"):
                        full_clip_url = f"{self.base_url}{raw_clip_url}"
                    else:
                        full_clip_url = raw_clip_url
                    
                    # กฎเหล็ก: ถ้า score > 0.80 ต้องส่ง metadata นี้เสมอ
                    is_high_priority = score > self.IRON_RULE_THRESHOLD
                    
                    results.append({
                        "type": "video",
                        "source": "Pinecone",
                        "id": match["id"],
                        "score": score,
                        "clip_url": raw_clip_url,
                        "full_url": full_clip_url,
                        "video_url": metadata.get("video_url"),
                        "transcript": metadata.get("transcript", ""),
                        "start_time": metadata.get("start_time"),
                        "end_time": metadata.get("end_time"),
                        "title": metadata.get("title", ""),
                        "quiz": metadata.get("quiz"),  # สำหรับ Academy Specialist
                        "reason": metadata.get("reason", ""),  # สำหรับ Journey Architect
                        "high_priority": is_high_priority,  # 🚨 กฎเหล็ก!
                        "circle": metadata.get("circle", 1)
                    })
                
                return results
                
        except Exception as e:
            print(f"❌ Pinecone search error: {e}")
            return []
    
    def hybrid_search(self, query: str) -> Dict[str, Any]:
        """
        🔍 HYBRID PARALLEL SEARCH (ตาม AGENTS.md)
        
        ในทุกครั้งที่มีคำถามเข้ามา ต้องรันระบบค้นหาแบบคู่ขนานเสมอ:
        1. ค้นหา Text จาก MEMORY.md (ฐานคำตอบหลัก)
        2. ค้นหา Vector จาก Pinecone (Namespace: highlights)
        
        กฎเหล็ก: แม้จะเจอคำตอบใน Text แล้ว 
                 แต่หากพบวิดีโอที่มี Similarity Score > 0.80
                 ห้ามทิ้ง! ต้องส่ง Metadata ไปกับชุดคำตอบเสมอ
        
        Returns:
            {
                "text_results": [...],      # จาก MEMORY.md
                "video_results": [...],     # จาก Pinecone
                "high_priority_videos": [...],  # Score > 0.80 (กฎเหล็ก!)
                "query": query,
                "total_text": N,
                "total_videos": N,
                "has_high_priority": bool   # มี video ที่ต้องส่งต่อเสมอ
            }
        """
        print(f"\n{'='*70}")
        print(f"🔍 HYBRID PARALLEL SEARCH: \"{query}\"")
        print(f"{'='*70}")
        
        # 1️⃣ ค้นหา Text จาก MEMORY.md (Parallel Task 1)
        print("📚 [1/2] Searching MEMORY.md...")
        text_results = self.search_memory_md(query)
        print(f"    ✅ Found {len(text_results)} text results")
        
        # 2️⃣ ค้นหา Vector จาก Pinecone (Parallel Task 2)
        print("🎬 [2/2] Searching Pinecone (highlights)...")
        embedding = self.generate_embedding(query)
        video_results = self.search_pinecone(embedding, top_k=5, min_score=0.05)
        print(f"    ✅ Found {len(video_results)} video results")
        
        # 3️⃣ กฎเหล็ก: ตรวจสอบ video ที่มี score > 0.80
        high_priority_videos = [
            v for v in video_results 
            if v.get("score", 0) > self.IRON_RULE_THRESHOLD
        ]
        
        print(f"\n🚨 IRON RULE CHECK:")
        print(f"    High priority videos (score > {self.IRON_RULE_THRESHOLD}): {len(high_priority_videos)}")
        
        for v in high_priority_videos:
            print(f"    ⚡ MUST SEND: {v['full_url'][:50]}... (score: {v['score']:.3f})")
        
        # 4️⃣ รวมผลลัพธ์
        result = {
            "query": query,
            "text_results": text_results,
            "video_results": video_results,
            "high_priority_videos": high_priority_videos,
            "total_text": len(text_results),
            "total_videos": len(video_results),
            "has_high_priority": len(high_priority_videos) > 0,
            "iron_rule_applied": True,  # บอก Journey Architect ว่าใช้กฎเหล็กแล้ว
            "metadata_for_journey_architect": {
                "videos": video_results,
                "high_priority": high_priority_videos,
                "recommendation": "nudge" if high_priority_videos else "text_or_video"
            }
        }
        
        print(f"\n{'='*70}")
        print(f"✅ HYBRID SEARCH COMPLETE")
        print(f"   Text: {len(text_results)} | Videos: {len(video_results)} | High Priority: {len(high_priority_videos)}")
        print(f"{'='*70}\n")
        
        return result
    
    def search_by_text(self, query: str) -> Dict[str, Any]:
        """
        🔍 Entry Point หลักสำหรับ Search Specialist
        
        เรียกใช้ hybrid_search() อัตโนมัติ
        """
        return self.hybrid_search(query)


# Test
if __name__ == "__main__":
    tool = SearchSpecialistTool()
    
    test_queries = ["ตรุษจีน", "ความรัก", "การให้อภัย"]
    
    print("="*70)
    print("🔍 Search Specialist Auto-Tool v2.0 - Hybrid Search Test")
    print("="*70)
    
    for query in test_queries:
        result = tool.hybrid_search(query)
        
        print(f"\n📊 Summary for '{query}':")
        print(f"   Text results: {result['total_text']}")
        print(f"   Video results: {result['total_videos']}")
        print(f"   High priority (score>0.80): {result['has_high_priority']}")
        
        if result['high_priority_videos']:
            print(f"\n   🚨 IRON RULE TRIGGERED!")
            for v in result['high_priority_videos']:
                print(f"      ⚡ {v['full_url'][:50]}... ({v['score']:.3f})")
