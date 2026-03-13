#!/usr/bin/env python3
"""
🧪 Workflow Simulation Test for Nong Unjai Swarm
ทดสอบ workflow: Search → Architect → Front-Desk → Media Delivery → LINE Gateway
"""

import asyncio
import sys
import json
from datetime import datetime

# Add paths
sys.path.insert(0, '/home/node/.openclaw/workspace-unjai')
sys.path.insert(0, '/home/node/.openclaw/workspace-unjai/modules')
sys.path.insert(0, '/home/node/.openclaw/workspace-unjai/docker/entrypoints')
sys.path.insert(0, '/home/node/.openclaw/workspace-unjai/tools')

# Mock classes for simulation
class MockSearchResult:
    """Mock Search Specialist results"""
    @staticmethod
    def get_video_results():
        return [
            {
                "id": "clip_001",
                "title": "ตรุษจีนกับคริสเตียน",
                "full_url": "https://nongaunjai.febradio.org/static/clips/1LXxKGOw6-8_2_34.mp4",
                "thumbnail": "https://img.youtube.com/vi/1LXxKGOw6-8/0.jpg",
                "score": 0.87,
                "transcript": "การเฉลิมฉลองตรุษจีนในฐานะคริสเตียน...",
                "video_url": "https://youtube.com/watch?v=1LXxKGOw6-8",
                "quiz": {"question": "คริสเตียนควรเฉลิมฉลองตรุษจีนหรือไม่?"}
            },
            {
                "id": "clip_002", 
                "title": "ความหมายของตรุษจีน",
                "full_url": "https://nongaunjai.febradio.org/static/clips/1LXxKGOw6-8_35_85.mp4",
                "thumbnail": "https://img.youtube.com/vi/1LXxKGOw6-8/1.jpg",
                "score": 0.72,
                "transcript": "ประวัติความเป็นมาของตรุษจีน...",
                "video_url": "https://youtube.com/watch?v=1LXxKGOw6-8"
            }
        ]
    
    @staticmethod
    def get_text_results():
        return {
            "content": "ตรุษจีนเป็นวัฒนธรรมที่สามารถเฉลิมฉลองได้ในฐานะคริสเตียน โดยเน้นความสามัคคีในครอบครัว",
            "source": "MEMORY.md"
        }


class SearchSpecialistAgent:
    """🕵️ Agent: Search Specialist (Squad 1)"""
    
    async def execute(self, query: str, user_id: str):
        print(f"\n{'='*60}")
        print("🔍 STEP 1: Search Specialist (Squad 1 - Knowledge & Retrieval)")
        print(f"{'='*60}")
        print(f"   Query: \"{query}\"")
        print(f"   User: {user_id}")
        print(f"   Action: Hybrid Parallel Search (MEMORY.md + Pinecone)")
        
        # Simulate search delay
        await asyncio.sleep(0.1)
        
        results = {
            "video_results": MockSearchResult.get_video_results(),
            "text_results": MockSearchResult.get_text_results(),
            "query": query
        }
        
        print(f"   ✅ Found {len(results['video_results'])} videos")
        print(f"   ✅ Found text content from {results['text_results']['source']}")
        
        return results


class JourneyArchitectAgent:
    """🏛️ Agent: Journey Architect (Squad 2)"""
    
    async def execute(self, message: str, search_results: dict):
        print(f"\n{'='*60}")
        print("🏛️ STEP 2: Journey Architect (Squad 2 - Governance & Strategy)")
        print(f"{'='*60}")
        print(f"   Input: Search results with {len(search_results.get('video_results', []))} videos")
        print(f"   Action: Analyze intent & R-score, make decision")
        
        # Simulate analysis
        await asyncio.sleep(0.1)
        
        videos = search_results.get("video_results", [])
        
        # Check for iron rule (score > 0.80)
        high_priority_videos = [v for v in videos if v.get("score", 0) > 0.80]
        
        if high_priority_videos:
            selected_video = high_priority_videos[0]
            decision = "video_package"
            reason = "iron_rule_high_priority"
            print(f"   🚨 IRON RULE triggered! Video score: {selected_video['score']:.2f}")
        elif videos and videos[0].get("score", 0) > 0.70:
            selected_video = videos[0]
            decision = "video_package"
            reason = "high_similarity_match"
        else:
            selected_video = None
            decision = "text_only"
            reason = "low_similarity"
        
        result = {
            "decision": decision,
            "selected_video": selected_video,
            "all_videos": videos,
            "text_content": search_results.get("text_results"),
            "reason": reason
        }
        
        print(f"   ✅ Decision: {decision}")
        print(f"   ✅ Reason: {reason}")
        if selected_video:
            print(f"   ✅ Selected Video: {selected_video['title']} (score: {selected_video['score']:.2f})")
        
        return result


class FrontDeskAgent:
    """🎙️ Agent: Front-Desk (Squad 3)"""
    
    async def execute(self, message: str, decision: dict, search_results: dict):
        print(f"\n{'='*60}")
        print("🎙️ STEP 3: Front-Desk (Squad 3 - Front-Desk & Pedagogy)")
        print(f"{'='*60}")
        print(f"   Input: Decision={decision['decision']}, Reason={decision['reason']}")
        print(f"   Action: Prepare response metadata (NOT building Flex Message)")
        
        await asyncio.sleep(0.1)
        
        decision_type = decision.get("decision", "text_only")
        selected_video = decision.get("selected_video")
        text_content = decision.get("text_content")
        reason = decision.get("reason", "")
        
        if decision_type in ["video_package", "video_nudge"] and selected_video:
            # ✅ CORRECT: Return video metadata only
            response = {
                "type": "video",  # Not "flex"
                "video_data": {
                    "title": selected_video.get("title", "คลิปหนุนใจ"),
                    "full_url": selected_video.get("full_url", ""),
                    "clip_url": selected_video.get("clip_url", selected_video.get("full_url", "")),
                    "thumbnail": selected_video.get("thumbnail", ""),
                    "video_url": selected_video.get("video_url", ""),
                    "score": selected_video.get("score", 0),
                    "transcript": selected_video.get("transcript", "")[:100],
                    "quiz": selected_video.get("quiz"),
                    "quiz_available": selected_video.get("quiz") is not None,
                },
                "alt_text": f"🎬 {selected_video.get('title', 'คลิปหนุนใจ')}",
                "metadata": {
                    "iron_rule_applied": reason == "iron_rule_high_priority",
                    "decision_type": decision_type
                }
            }
            
            if text_content:
                response["text_supplement"] = text_content.get("content", "")[:200]
            
            print(f"   ✅ Response Type: video (metadata only)")
            print(f"   ✅ Video Title: {response['video_data']['title']}")
            print(f"   ✅ Score: {response['video_data']['score']:.2f}")
            
        else:
            response = {
                "type": "text",
                "content": f"{text_content.get('content', '')[:500]}...\n\n💕 จากน้องอุ่นใจ"
            }
            print(f"   ✅ Response Type: text")
        
        return response


class MediaDeliveryAgent:
    """🎬 Agent: Media Delivery (Squad 4)"""
    
    def __init__(self):
        # Import FlexMessageBuilder
        try:
            from flex_templates import FlexMessageBuilder
            self.builder = FlexMessageBuilder()
            self.has_builder = True
        except ImportError:
            self.has_builder = False
            print("   ⚠️  FlexMessageBuilder not available, using mock")
    
    async def execute(self, response: dict):
        print(f"\n{'='*60}")
        print("🎬 STEP 4: Media Delivery (Squad 4 - Content Integrity & Delivery)")
        print(f"{'='*60}")
        
        media_type = response.get("type")
        print(f"   Input Type: {media_type}")
        print(f"   Action: Build Flex Message from metadata")
        
        await asyncio.sleep(0.1)
        
        if media_type == "video":
            video_data = response.get("video_data", {})
            decision_type = response.get("metadata", {}).get("decision_type", "video_package")
            
            # ✅ CORRECT: Build Flex Message here
            if self.has_builder:
                if decision_type == "video_nudge":
                    flex_content = self.builder.create_video_nudge(video_data)
                    print(f"   ✅ Built: Video NUDGE Flex Message")
                else:
                    flex_content = self.builder.create_video_card(video_data)
                    print(f"   ✅ Built: Video CARD Flex Message")
            else:
                # Mock flex content
                flex_content = {
                    "type": "bubble",
                    "hero": {"type": "image", "url": video_data.get("thumbnail", "")},
                    "body": {"type": "box", "contents": [{"type": "text", "text": video_data.get("title", "")}]},
                    "footer": {"type": "box", "contents": [{"type": "button", "action": {"type": "uri", "uri": video_data.get("full_url", "")}}]}
                }
                print(f"   ✅ Built: Mock Flex Message (FlexMessageBuilder not available)")
            
            # Validate
            if flex_content.get("type") == "bubble":
                print(f"   ✅ Validation: Flex bubble structure OK")
            
            result = {
                "status": "delivered",
                "type": "flex",
                "content": flex_content,
                "alt_text": response.get("alt_text", "🎬 คลิปหนุนใจ"),
                "metadata": response.get("metadata", {})
            }
            
            print(f"   ✅ Final Output Type: flex")
            
        elif media_type == "text":
            result = {
                "status": "delivered",
                "type": "text",
                "content": response.get("content", "")
            }
            print(f"   ✅ Final Output Type: text")
        else:
            result = {"status": "error", "error": f"Unknown type: {media_type}"}
            print(f"   ❌ Error: Unknown type")
        
        return result


class LineGateway:
    """📱 LINE Gateway (Final Step)"""
    
    async def send_to_user(self, response: dict):
        print(f"\n{'='*60}")
        print("📱 STEP 5: LINE Gateway (Final Delivery)")
        print(f"{'='*60}")
        
        msg_type = response.get("type")
        
        if msg_type == "flex":
            flex_content = response.get("content", {})
            print(f"   Action: Send Flex Message to LINE user")
            print(f"   Alt Text: {response.get('alt_text', '')}")
            
            # Show structure
            print(f"\n   📋 Flex Message Structure:")
            print(f"   ├── Type: {flex_content.get('type')}")
            print(f"   ├── Hero: {flex_content.get('hero', {}).get('type')} image")
            print(f"   ├── Body: {len(flex_content.get('body', {}).get('contents', []))} elements")
            if flex_content.get('footer'):
                print(f"   └── Footer: {len(flex_content.get('footer', {}).get('contents', []))} buttons")
            
        elif msg_type == "text":
            print(f"   Action: Send Text Message")
            print(f"   Preview: {response.get('content', '')[:80]}...")
        
        print(f"\n   ✅ Message sent to user successfully!")
        
        return {"status": "sent", "timestamp": datetime.now().isoformat()}


async def run_simulation(query: str):
    """Run full workflow simulation"""
    
    print("\n" + "="*60)
    print("🧪 NONG UNJAI SWARM WORKFLOW SIMULATION")
    print("="*60)
    print(f"\n📨 User Query: \"{query}\"")
    
    user_id = "test_user_123"
    
    # Initialize agents
    search_agent = SearchSpecialistAgent()
    architect_agent = JourneyArchitectAgent()
    front_desk = FrontDeskAgent()
    media_delivery = MediaDeliveryAgent()
    gateway = LineGateway()
    
    try:
        # Step 1: Search
        search_results = await search_agent.execute(query, user_id)
        
        # Step 2: Journey Architect Decision
        decision = await architect_agent.execute(query, search_results)
        
        # Step 3: Front-Desk Response Planning
        front_desk_response = await front_desk.execute(query, decision, search_results)
        
        # Step 4: Media Delivery (if video)
        if front_desk_response.get("type") == "video":
            final_response = await media_delivery.execute(front_desk_response)
        else:
            final_response = front_desk_response
        
        # Step 5: LINE Gateway
        result = await gateway.send_to_user(final_response)
        
        # Summary
        print("\n" + "="*60)
        print("✅ SIMULATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\n📊 Workflow Summary:")
        print(f"   1. Search Specialist: Found {len(search_results['video_results'])} videos")
        print(f"   2. Journey Architect: Decision={decision['decision']}, Reason={decision['reason']}")
        print(f"   3. Front-Desk: Returned {front_desk_response['type']} metadata")
        if front_desk_response.get("type") == "video":
            print(f"   4. Media Delivery: Built {final_response['type']} message")
        else:
            print(f"   4. Media Delivery: Skipped (text only)")
        print(f"   5. LINE Gateway: {result['status']}")
        
        print(f"\n🔍 AGENTS.md Squad 4 Compliance:")
        print(f"   ✅ Media Delivery Agent builds Flex Message")
        print(f"   ✅ Front-Desk returns metadata (not built flex)")
        print(f"   ✅ Responsibility separation clear")
        
        return True
        
    except Exception as e:
        print(f"\n❌ SIMULATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Workflow Simulation...\n")
    
    # Test queries
    test_queries = [
        "ตรุษจีนกับคริสเตียน",
        "บาปได้รับมรดกเป็นความตาย"
    ]
    
    for query in test_queries:
        success = asyncio.run(run_simulation(query))
        print("\n" + "="*60)
        print("Press Enter for next test..." if query != test_queries[-1] else "Done!")
        print("="*60)
        if query != test_queries[-1]:
            input()
