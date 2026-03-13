import os
import json
import asyncio
from typing import Dict, Any, Optional

# Mock UserSession for testing
class UserSession:
    def __init__(self, user_id: str, current_circle: int = 1):
        self.user_id = user_id
        self.current_circle = current_circle

# Import our connectors
# We'll use a local import trick since we're in the same directory but need to mock settings if needed
import sys
sys.path.append(os.path.join(os.getcwd(), 'modules'))

from line_orchestrator import SearchSpecialistConnector

async def verify_filtering():
    print("🧪 Verifying Session-Aware Pinecone Search...")
    
    connector = SearchSpecialistConnector()
    
    # Test case 1: User in Circle 1 (Self)
    print("\n--- Test Case 1: Circle 1 User ---")
    session1 = UserSession("user_c1", current_circle=1)
    # We'll mock the internal search_pinecone to see what filter it gets
    
    original_search = connector.search_pinecone
    
    captured_filter = None
    async def mock_search(embedding, top_k=3, min_score=0.7, filter=None):
        nonlocal captured_filter
        captured_filter = filter
        return [] # Return empty for test
        
    connector.search_pinecone = mock_search
    
    await connector.parallel_search("hello", session=session1)
    
    print(f"Captured Filter for Circle 1: {json.dumps(captured_filter)}")
    assert captured_filter == {"circle": {"$lte": 1}}, f"Expected circle <= 1, got {captured_filter}"
    print("✅ Circle 1 Filtering Logic OK")
    
    # Test case 2: User in Circle 3 (Society)
    print("\n--- Test Case 2: Circle 3 User ---")
    session3 = UserSession("user_c3", current_circle=3)
    
    await connector.parallel_search("hello", session=session3)
    
    print(f"Captured Filter for Circle 3: {json.dumps(captured_filter)}")
    assert captured_filter == {"circle": {"$lte": 3}}, f"Expected circle <= 3, got {captured_filter}"
    print("✅ Circle 3 Filtering Logic OK")
    
    # Reset connector for actual search test if keys are present
    connector.search_pinecone = original_search
    
    if os.getenv("PINECONE_API_KEY") and os.getenv("OPENAI_API_KEY"):
        print("\n--- Test Case 3: Real Search (requires APIs) ---")
        try:
            results = await connector.parallel_search("กำลังใจ", session=session1)
            print(f"Real Search Results (Circle 1): {len(results.get('video_results', []))} videos")
            if results.get('video_results'):
                for v in results['video_results'][:2]:
                    print(f" - [{v['id']}] Score: {v['score']:.3f}")
        except Exception as e:
            print(f"⚠️ Real search test failed (maybe keys are invalid or index is down): {e}")
    else:
        print("\n⏭️ Skipping real search test (API keys not found in current shell)")

if __name__ == "__main__":
    asyncio.run(verify_filtering())
