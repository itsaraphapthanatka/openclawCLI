#!/usr/bin/env python3
"""
Check specific video in Pinecone
ตรวจสอบว่าคลิปตรุษจีน (1LXxKGOw6-8) อยู่ใน Pinecone หรือไม่
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

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_HOST = os.getenv("PINECONE_INDEX_HOST")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "highlights")
BASE_URL = os.getenv("BASE_URL", "https://nongaunjai.febradio.org")

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

print("="*70)
print("🔍 Checking Specific Video: 1LXxKGOw6-8 (ตรุษจีน)")
print("="*70)

# MD5 hashes for the 7 clips
clip_ids = [
    "185676268eac9e7a8b1d71890bbc4509",
    "04148410b2f3d78b5efcb8f73195c50c",
    "2bf1830e3a1dcfa9d554f09917f10d59",
    "ca078d2e5a2f4b69da7cf351ebaf1663",
    "2393c5bd47e2ce85d58d500e19e05a1a",
    "b2373fd6595a6716252f22dae1d86791",
    "35dc59b82ee2d4a287cc83fe1f7a62cc"
]

print(f"\n📋 Looking for {len(clip_ids)} clips...")

found_count = 0
for clip_id in clip_ids:
    try:
        # Fetch vector by ID
        req = urllib.request.Request(
            f"{PINECONE_INDEX_HOST}/vectors/fetch",
            data=json.dumps({
                "namespace": PINECONE_NAMESPACE,
                "ids": [clip_id]
            }).encode('utf-8'),
            headers={
                "Api-Key": PINECONE_API_KEY,
                "Content-Type": "application/json"
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            vectors = data.get("vectors", {})
            
            if clip_id in vectors:
                found_count += 1
                meta = vectors[clip_id].get("metadata", {})
                print(f"\n  ✅ Found: {clip_id[:20]}...")
                print(f"     Video ID: {meta.get('video_id', 'N/A')}")
                print(f"     Clip URL: {meta.get('clip_url', 'N/A')}")
                print(f"     Transcript: {meta.get('transcript', 'N/A')[:60]}...")
            else:
                print(f"  ❌ Not found: {clip_id[:20]}...")
                
    except Exception as e:
        print(f"  ❌ Error checking {clip_id[:20]}...: {e}")

print(f"\n{'='*70}")
print(f"Summary: Found {found_count}/{len(clip_ids)} clips")
print("="*70)

# Also check total count
print("\n📊 Checking total vectors in index...")
try:
    req = urllib.request.Request(
        f"{PINECONE_INDEX_HOST}/describe_index_stats",
        headers={"Api-Key": PINECONE_API_KEY},
        method='GET'
    )
    
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        namespaces = data.get("namespaces", {})
        highlights = namespaces.get(PINECONE_NAMESPACE, {})
        print(f"   Total vectors in '{PINECONE_NAMESPACE}': {highlights.get('vectorCount', 0)}")
        
except Exception as e:
    print(f"   Error: {e}")

print("="*70)
