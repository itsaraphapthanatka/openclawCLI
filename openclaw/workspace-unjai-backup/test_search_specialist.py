#!/usr/bin/env python3
"""
Test Search Specialist - End to End
ทดสอบการค้นหา Pinecone แบบสมบูรณ์
"""
import os
import sys
import asyncio
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / "docker" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

sys.path.insert(0, str(Path(__file__).parent / "modules"))

from line_orchestrator import SearchSpecialistConnector, LineOrchestrator

async def test_search():
    """ทดสอบการค้นหา"""
    print("="*70)
    print("🔍 Testing Search Specialist - Pinecone Search")
    print("="*70)
    
    # Create connector
    connector = SearchSpecialistConnector()
    
    print(f"\n📋 Configuration:")
    print(f"   Index Host: {connector.index_host}")
    print(f"   Namespace: {connector.namespace}")
    print(f"   Base URL: {connector.base_url}")
    print(f"   OpenAI Key: {'SET' if connector.openai_api_key else 'NOT SET'}")
    
    # Test queries
    test_queries = [
        "ตรุษจีน",
        "ความรัก",
        "การให้อภัย",
        "ความหวัง"
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"🔍 Query: \"{query}\"")
        print("="*70)
        
        try:
            results = await connector.search_pinecone_by_text(query, top_k=3, min_score=0.70)
            
            print(f"✅ Found {len(results)} results")
            
            for i, video in enumerate(results[:2], 1):
                print(f"\n  Result {i}:")
                print(f"    ID: {video['id'][:30]}...")
                print(f"    Score: {video['score']:.3f}")
                print(f"    Clip URL: {video['clip_url'][:60]}...")
                print(f"    Transcript: {video['transcript'][:80]}...")
                
                # Verify full URL
                if video['clip_url'].startswith('https://nongaunjai.febradio.org'):
                    print(f"    ✅ URL has correct base")
                else:
                    print(f"    ❌ URL missing base URL!")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("✅ Test complete")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_search())
