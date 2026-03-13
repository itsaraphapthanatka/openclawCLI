#!/usr/bin/env python3
"""
Session Debug Viewer - แสดงทุก Session ที่มีการถามตอบ
ใช้สำหรับ Debug ว่า clip_url ถูกต้องหรือไม่
"""
import os
import sys
import json
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from session_debugger import get_debugger, print_session_summary
from pinecone_connector import get_connector

def test_url_transformation():
    """ทดสอบการแปลง URL"""
    print("\n" + "="*70)
    print("🧪 Testing URL Transformation")
    print("="*70)
    
    base_url = os.getenv("BASE_URL", "https://nongaunjai.febradio.org")
    print(f"Base URL from .env: {base_url}")
    
    # Test cases
    test_urls = [
        "/static/clips/test123.mp4",
        "https://nongaunjai.febradio.org/static/clips/test456.mp4",
        "http://example.com/video.mp4",
    ]
    
    print("\nTest URL Transformations:")
    for url in test_urls:
        if url.startswith("/"):
            full_url = f"{base_url}{url}"
        else:
            full_url = url
        print(f"  Input:  {url}")
        print(f"  Output: {full_url}")
        print(f"  ✅ Correct: {full_url.startswith(base_url) or not url.startswith('/')}")
        print()

def show_pinecone_samples():
    """แสดงตัวอย่างข้อมูลจาก Pinecone"""
    print("\n" + "="*70)
    print("🎬 Pinecone Sample Records")
    print("="*70)
    
    connector = get_connector()
    samples = connector.get_sample_records(3)
    
    if not samples:
        print("⚠️ No samples found in Pinecone")
        return
    
    print(f"Found {len(samples)} sample records:\n")
    
    for i, video in enumerate(samples, 1):
        print(f"  {i}. ID: {video.id}")
        print(f"     Clip URL: {video.clip_url}")
        print(f"     Has Base URL: {video.clip_url.startswith('https://nongaunjai.febradio.org')}")
        print(f"     Score: {video.score:.3f}")
        print(f"     Reason: {video.reason[:50]}...")
        print()

def show_session_debug():
    """แสดงข้อมูล Debug ของ Sessions"""
    print("\n" + "="*70)
    print("📊 Session Debug Information")
    print("="*70)
    
    print_session_summary()

def main():
    """Main function"""
    print("="*70)
    print("🔍 Nong Unjai Session Debug Tool")
    print("="*70)
    print(f"BASE_URL: {os.getenv('BASE_URL', 'NOT SET')}")
    print(f"PINECONE_INDEX: {os.getenv('PINECONE_INDEX_NAME', 'NOT SET')}")
    print()
    
    # Run tests
    test_url_transformation()
    show_pinecone_samples()
    show_session_debug()
    
    print("\n" + "="*70)
    print("✅ Debug complete")
    print("="*70)

if __name__ == "__main__":
    main()
