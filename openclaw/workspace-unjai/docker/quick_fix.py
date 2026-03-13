#!/usr/bin/env python3
"""
Quick fix script - Run this inside the Docker container
"""
import os
import sys

print("="*70)
print("🔧 Quick Fix - Checking Environment")
print("="*70)

# Check critical variables
vars_needed = [
    "PINECONE_API_KEY",
    "PINECONE_INDEX_HOST", 
    "PINECONE_NAMESPACE",
    "BASE_URL"
]

print("\n📋 Checking Environment Variables:")
for var in vars_needed:
    val = os.getenv(var)
    if val:
        print(f"  ✅ {var}: {val[:30]}..." if len(str(val)) > 30 else f"  ✅ {var}: {val}")
    else:
        print(f"  ❌ {var}: NOT SET")

# Try to import and test
print("\n🌐 Testing Pinecone Connection:")
try:
    sys.path.insert(0, '/app/modules')
    from pinecone_connector import get_connector
    
    connector = get_connector()
    print(f"  ✅ Connector created")
    print(f"     Base URL: {connector.BASE_URL}")
    
    # Test with sample
    samples = connector.get_sample_records(1)
    print(f"  ✅ Got {len(samples)} samples")
    
    if samples:
        print(f"\n  📹 First sample:")
        print(f"     ID: {samples[0].id}")
        print(f"     Clip URL: {samples[0].clip_url}")
        
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✅ Check complete")
print("="*70)
