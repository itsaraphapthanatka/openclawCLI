#!/usr/bin/env python3
"""
Test Pinecone with Real Embedding
ทดสอบการค้นหา Pinecone ด้วย embedding จริง
"""
import os
import sys
import json
import ssl
import urllib.request
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / "docker" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

print("="*70)
print("🔍 Pinecone Search with Real Embedding")
print("="*70)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_HOST = os.getenv("PINECONE_INDEX_HOST")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "highlights")
BASE_URL = os.getenv("BASE_URL", "https://nongaunjai.febradio.org")

print(f"\n📋 Config:")
print(f"   OpenAI Key: {'SET (' + OPENAI_API_KEY[:20] + '...)' if OPENAI_API_KEY else 'NOT SET'}")
print(f"   Pinecone Key: {'SET' if PINECONE_API_KEY else 'NOT SET'}")
print(f"   Index Host: {PINECONE_INDEX_HOST}")
print(f"   Namespace: {PINECONE_NAMESPACE}")

# Test queries
queries = ["ตรุษจีน", "ความรัก", "การให้อภัย"]

for query in queries:
    print(f"\n{'='*70}")
    print(f"🔍 Query: \"{query}\"")
    print("="*70)
    
    # 1. Generate embedding with OpenAI
    try:
        print("   🔄 Generating embedding...")
        
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            "https://api.openai.com/v1/embeddings",
            data=json.dumps({
                "model": "text-embedding-3-small",
                "input": query,
                "dimensions": 384
            }).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            embedding = data["data"][0]["embedding"]
            print(f"   ✅ Embedding generated: {len(embedding)} dimensions")
    
    except Exception as e:
        print(f"   ❌ Embedding failed: {e}")
        continue
    
    # 2. Search Pinecone
    try:
        print("   🔄 Searching Pinecone...")
        
        req = urllib.request.Request(
            f"{PINECONE_INDEX_HOST}/query",
            data=json.dumps({
                "namespace": PINECONE_NAMESPACE,
                "vector": embedding,
                "topK": 3,
                "includeMetadata": True,
                "includeValues": False
            }).encode('utf-8'),
            headers={
                "Api-Key": PINECONE_API_KEY,
                "Content-Type": "application/json"
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            matches = data.get("matches", [])
            
            print(f"   ✅ Found {len(matches)} matches")
            
            if matches:
                for i, match in enumerate(matches[:2], 1):
                    meta = match.get("metadata", {})
                    clip_url = meta.get("clip_url", "N/A")
                    full_url = f"{BASE_URL}{clip_url}" if clip_url.startswith("/") else clip_url
                    
                    print(f"\n   Result {i}:")
                    print(f"     ID: {match['id'][:30]}...")
                    print(f"     Score: {match.get('score', 0):.3f}")
                    print(f"     Clip: {clip_url}")
                    print(f"     Full: {full_url}")
                    print(f"     Title: {meta.get('title', 'N/A')[:50]}...")
            else:
                print("   ⚠️  No matches found (score too low or no data)")
                
    except Exception as e:
        print(f"   ❌ Pinecone search failed: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*70)
print("✅ Test complete")
print("="*70)
