#!/usr/bin/env python3
"""
Pinecone Connection Diagnostic Tool
ใช้ตรวจสอบว่าเชื่อมต่อ Pinecone ได้หรือไม่
"""
import os
import sys
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / "modules"))

print("="*70)
print("🔍 Pinecone Connection Diagnostic")
print("="*70)

# 1. Check environment variables
print("\n📋 Environment Variables:")
required_vars = {
    "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
    "PINECONE_INDEX_HOST": os.getenv("PINECONE_INDEX_HOST"),
    "PINECONE_NAMESPACE": os.getenv("PINECONE_NAMESPACE", "highlights"),
    "BASE_URL": os.getenv("BASE_URL", "https://nongaunjai.febradio.org"),
}

all_set = True
for var_name, value in required_vars.items():
    if value:
        if "KEY" in var_name:
            display = value[:20] + "..." if len(value) > 20 else value
        else:
            display = value
        print(f"  ✅ {var_name}: {display}")
    else:
        print(f"  ❌ {var_name}: NOT SET")
        all_set = False

if not all_set:
    print("\n⚠️  Please set all required environment variables in .env file")
    print("   Example:")
    print('   PINECONE_API_KEY=pcsk_...')
    print('   PINECONE_INDEX_HOST=https://aunjai-knowledge-...')
    sys.exit(1)

# 2. Test Pinecone connection
print("\n🌐 Testing Pinecone Connection...")
try:
    from pinecone_connector import get_connector
    
    connector = get_connector()
    print(f"  ✅ Connector initialized")
    print(f"     Base URL: {connector.BASE_URL}")
    print(f"     Namespace: {connector.namespace}")
    
    # Try to get sample records
    print("\n📊 Fetching sample records...")
    samples = connector.get_sample_records(2)
    
    if samples:
        print(f"  ✅ Successfully fetched {len(samples)} samples")
        for i, video in enumerate(samples, 1):
            print(f"\n     Sample {i}:")
            print(f"       ID: {video.id}")
            print(f"       Clip URL: {video.clip_url}")
            print(f"       Score: {video.score:.3f}")
    else:
        print("  ⚠️  No samples found (index might be empty)")
        
except Exception as e:
    print(f"  ❌ Connection failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Test search
print("\n🔍 Testing search functionality...")
try:
    results = connector.search_by_text("ตรุษจีน", top_k=3, min_score=0.70)
    print(f"  ✅ Search returned {len(results)} results")
    
    for i, video in enumerate(results[:2], 1):
        print(f"\n     Result {i}:")
        print(f"       ID: {video.id}")
        print(f"       Clip URL: {video.clip_url}")
        print(f"       Score: {video.score:.3f}")
        print(f"       Has full URL: {video.clip_url.startswith('https://')}")
        
except Exception as e:
    print(f"  ❌ Search failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✅ Diagnostic complete")
print("="*70)
