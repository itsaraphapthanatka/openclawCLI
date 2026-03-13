#!/usr/bin/env python3
"""
Pinecone Connection Diagnostic (No external deps)
ตรวจสอบการเชื่อมต่อ Pinecone Vector Database
"""
import os
import sys
import json
import ssl
import urllib.request

print("="*70)
print("🔍 Pinecone Connection Diagnostic")
print("="*70)

# 1. Check environment variables
print("\n📋 Environment Variables:")
required_vars = {
    "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
    "PINECONE_INDEX_HOST": os.getenv("PINECONE_INDEX_HOST"),
    "PINECONE_NAMESPACE": os.getenv("PINECONE_NAMESPACE"),
    "BASE_URL": os.getenv("BASE_URL"),
}

all_set = True
for var_name, value in required_vars.items():
    if value:
        if "KEY" in var_name:
            display = value[:30] + "..." if len(str(value)) > 30 else value
        else:
            display = value
        print(f"  ✅ {var_name}: {display}")
    else:
        print(f"  ❌ {var_name}: NOT SET")
        all_set = False

if not all_set:
    print("\n⚠️  Trying to load from docker/.env file...")
    # Try to read from file directly
    try:
        with open('docker/.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val
        print("  ✅ Loaded from docker/.env")
        
        # Check again
        for var_name, value in required_vars.items():
            val = os.getenv(var_name)
            if val:
                print(f"  ✅ {var_name}: {val[:40] if 'KEY' in var_name else val}...")
            else:
                print(f"  ❌ {var_name}: Still not set")
    except Exception as e:
        print(f"  ❌ Failed to load .env: {e}")
        sys.exit(1)

# 2. Test Pinecone connection
print("\n🌐 Testing Pinecone Connection...")

api_key = os.getenv("PINECONE_API_KEY")
index_host = os.getenv("PINECONE_INDEX_HOST")
namespace = os.getenv("PINECONE_NAMESPACE", "highlights")

try:
    # SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Test query with dummy vector (384 dimensions)
    url = f"{index_host}/query"
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Create dummy embedding (384 dimensions of zeros)
    dummy_vector = [0.0] * 384
    
    payload = json.dumps({
        "namespace": namespace,
        "vector": dummy_vector,
        "topK": 3,
        "includeMetadata": True,
        "includeValues": False
    }).encode('utf-8')
    
    print(f"  📡 Connecting to: {index_host}")
    print(f"  📁 Namespace: {namespace}")
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers=headers,
        method='POST'
    )
    
    with urllib.request.urlopen(req, context=ssl_context, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        matches = data.get("matches", [])
        
        print(f"\n  ✅ Connection successful!")
        print(f"  📊 Found {len(matches)} vectors in index")
        
        if matches:
            print(f"\n  📹 Sample records:")
            for i, match in enumerate(matches[:2], 1):
                metadata = match.get("metadata", {})
                clip_url = metadata.get("clip_url", "N/A")
                
                # Add base URL if needed
                base_url = os.getenv("BASE_URL", "https://nongaunjai.febradio.org")
                if clip_url.startswith("/"):
                    full_url = f"{base_url}{clip_url}"
                else:
                    full_url = clip_url
                
                print(f"\n    Record {i}:")
                print(f"      ID: {match['id'][:30]}...")
                print(f"      Score: {match.get('score', 0):.3f}")
                print(f"      Clip URL: {clip_url}")
                print(f"      Full URL: {full_url[:60]}...")
                print(f"      Title: {metadata.get('title', 'N/A')[:40]}...")
        
        print("\n" + "="*70)
        print("✅ Pinecone is CONNECTED and READY!")
        print("="*70)
        
except urllib.error.HTTPError as e:
    print(f"\n  ❌ HTTP Error: {e.code} - {e.reason}")
    try:
        error_body = e.read().decode('utf-8')
        print(f"  Response: {error_body}")
    except:
        pass
    print("\n" + "="*70)
    print("❌ Pinecone connection FAILED!")
    print("="*70)
    sys.exit(1)
    
except urllib.error.URLError as e:
    print(f"\n  ❌ URL Error: {e.reason}")
    print("\n" + "="*70)
    print("❌ Pinecone connection FAILED!")
    print("="*70)
    sys.exit(1)
    
except Exception as e:
    print(f"\n  ❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*70)
    print("❌ Pinecone connection FAILED!")
    print("="*70)
    sys.exit(1)
