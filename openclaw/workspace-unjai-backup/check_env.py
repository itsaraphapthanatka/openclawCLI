#!/usr/bin/env python3
"""
Quick diagnostic script to check if BASE_URL is loaded correctly
Run this inside the Docker container to verify environment variables
"""
import os

print("="*70)
print("🔍 Environment Variable Diagnostic")
print("="*70)

# Check critical environment variables
vars_to_check = [
    ("BASE_URL", "https://nongaunjai.febradio.org"),
    ("PINECONE_API_KEY", None),
    ("PINECONE_INDEX_HOST", None),
    ("PINECONE_NAMESPACE", "highlights"),
    ("LINE_CHANNEL_ACCESS_TOKEN", None),
]

print("\n📋 Environment Variables:")
for var_name, default in vars_to_check:
    value = os.getenv(var_name)
    if value:
        # Mask sensitive values
        if "TOKEN" in var_name or "KEY" in var_name or "SECRET" in var_name:
            display = value[:20] + "..." if len(value) > 20 else value
        else:
            display = value
        print(f"  ✅ {var_name}: {display}")
    else:
        print(f"  ❌ {var_name}: NOT SET (default: {default})")

# Test URL construction
print("\n🔗 URL Construction Test:")
base_url = os.getenv("BASE_URL", "https://nongaunjai.febradio.org")
test_clip = "/static/clips/test123.mp4"
full_url = f"{base_url}{test_clip}"
print(f"  Input:  {test_clip}")
print(f"  Output: {full_url}")
print(f"  ✅ URL looks correct: {full_url.startswith('https://')}")

print("\n" + "="*70)
