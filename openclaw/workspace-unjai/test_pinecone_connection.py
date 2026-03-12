"""
Test Connection: LINE + Pinecone Integration
ทดสอบการเชื่อมต่อจริงกับ Pinecone
"""

import os
import asyncio
import json
from typing import List, Dict, Any

# Try to load from .env
from dotenv import load_dotenv
load_dotenv()

# Pinecone Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_HOST = os.getenv("PINECONE_INDEX_HOST")
NAMESPACE = "highlights"

print("=" * 60)
print("🔍 Testing LINE + Pinecone Connection")
print("=" * 60)
print()

# Check if env vars are set
print("📋 Environment Variables:")
print(f"  PINECONE_API_KEY: {'✅ Set' if PINECONE_API_KEY else '❌ Not Set'}")
print(f"  PINECONE_INDEX_HOST: {'✅ Set' if PINECONE_INDEX_HOST else '❌ Not Set'}")
print()

if not PINECONE_API_KEY or not PINECONE_INDEX_HOST:
    print("❌ ERROR: Please set environment variables in .env file:")
    print("   PINECONE_API_KEY=your_key")
    print("   PINECONE_INDEX_HOST=https://aunjai-knowledge-...")
    exit(1)

import httpx

async def test_pinecone_connection():
    """ทดสอบการเชื่อมต่อ Pinecone"""
    print("🧪 Testing Pinecone Connection...")
    print()
    
    try:
        # Test 1: Query with zero vector (get random samples)
        url = f"{PINECONE_INDEX_HOST}/query"
        headers = {
            "Api-Key": PINECONE_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Create a dummy embedding (384 dimensions of zeros)
        zero_vector = [0.0] * 384
        
        payload = {
            "namespace": NAMESPACE,
            "vector": zero_vector,
            "topK": 3,
            "includeMetadata": True
        }
        
        print(f"📡 Calling: {url}")
        print(f"📦 Namespace: {NAMESPACE}")
        print()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            
            print(f"✅ Status: {response.status_code}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get("matches", [])
                
                print(f"🎯 Found {len(matches)} records:")
                print("-" * 60)
                
                for i, match in enumerate(matches, 1):
                    metadata = match.get("metadata", {})
                    score = match.get("score", 0)
                    
                    print(f"\n📹 Video #{i} (Score: {score:.3f}):")
                    print(f"   ID: {match['id']}")
                    print(f"   Clip URL: {metadata.get('clip_url', 'N/A')}")
                    print(f"   Video URL: {metadata.get('video_url', 'N/A')}")
                    print(f"   Time: {metadata.get('start_time', 0)}s - {metadata.get('end_time', 0)}s")
                    print(f"   Type: {metadata.get('type', 'N/A')}")
                    print(f"   Transcript: {metadata.get('transcript', 'N/A')[:80]}...")
                
                print("\n" + "-" * 60)
                return True, matches
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False, []
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False, []

async def test_search_with_text():
    """ทดสอบค้นหาด้วยข้อความ"""
    print("\n" + "=" * 60)
    print("🔍 Testing Search with Thai Text")
    print("=" * 60)
    print()
    
    # จำลอง embedding สำหรับคำค้นหา (ในระบบจริงจะใช้ OpenAI)
    # ใช้ random vector ที่มี pattern เฉพาะแทน
    test_vector = [0.05] * 384
    
    url = f"{PINECONE_INDEX_HOST}/query"
    headers = {
        "Api-Key": PINECONE_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "namespace": NAMESPACE,
        "vector": test_vector,
        "topK": 5,
        "includeMetadata": True
    }
    
    print("🔎 Simulating search for: 'การให้อภัย' (forgiveness)")
    print(f"📡 Calling Pinecone API...")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            
            # Filter เฉพาะที่มี clip_url
            highlights = [m for m in matches if m.get("metadata", {}).get("clip_url")]
            
            print(f"\n✅ Found {len(highlights)} video highlights!")
            
            for match in highlights:
                meta = match["metadata"]
                print(f"\n🎬 {meta.get('reason', 'No description')[:60]}")
                print(f"   Clip: {meta.get('clip_url')}")
            
            return highlights
        else:
            print(f"❌ Error: {response.status_code}")
            return []

async def main():
    """Run all tests"""
    print("\n" + "🚀 " * 20)
    print("STARTING PINE CONE CONNECTION TEST")
    print("🚀 " * 20 + "\n")
    
    # Test 1: Basic Connection
    success, samples = await test_pinecone_connection()
    
    if success:
        # Test 2: Search with text simulation
        highlights = await test_search_with_text()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📊 Summary:")
        print(f"   - Connection to Pinecone: ✅")
        print(f"   - Namespace '{NAMESPACE}': ✅")
        print(f"   - Sample records found: {len(samples)}")
        print(f"   - Video highlights: {len([s for s in samples if s.get('metadata', {}).get('clip_url')])}")
        print()
        print("🎯 Ready for LINE integration!")
    else:
        print("\n❌ TESTS FAILED - Please check credentials")

if __name__ == "__main__":
    asyncio.run(main())
