🛠️ TOOLS.md: Technical Payloads & Operational Logic (v3.0 Middleware-Centric)ไฟล์นี้คือ "หัวใจเชิงเทคนิค" ที่บรรจุชุดคำสั่ง JSON สำหรับ 6 Squads เพื่อควบคุมการทำงานของ 15 Agents ผ่าน Middleware Master Brain 🏛️ Phase 1: Knowledge Foundation (The Brain)Agents: Archivist, Search SpecialistLogic: Hybrid Parallel Search with Intent Extraction JSON{
  "knowledge_engine": {
    "vector_db_config": {
      "provider": "Pinecone",
      "index_name": "aunjai-knowledge",
      "host": "https://aunjai-knowledge-3ygam8j.svc.aped-4627-b74a.pinecone.io",
      "namespace": "highlights",
      "dimension": 1536
    },
    "search_logic": {
      "type": "Hybrid_Parallel_Search",
      "query_refinement": "Extract_Core_Intent_Only",
      "min_similarity_score": 0.87,
      "always_return_video_metadata": true,
      "parallel_execution": {
        "source_1": "MEMORY.md_Text",
        "source_2": "Pinecone_Vector"
      }
    },
    "chunking_strategy": {
      "method": "Semantic_Chunking",
      "max_characters": 400,
      "metadata_schema": ["clip_url", "thumbnail", "transcript", "quiz", "score", "circle"]
    }
  }
}
🛡️ Phase 2: Governance & Dynamic Routing (The Strategy)Agents: Journey Architect, SentinelLogic: Circle as a Service & High-Precision Bypass JSON{
  "governance_logic": {
    "dynamic_routing": {
      "priority": "Intent_Over_Score",
      "modes": {
        "C1_Healing": "If Intent = Emotional_Venting or Sentiment < -0.4",
        "C2_Wisdom": "If Intent = Faith_Question or Growth_Seeking",
        "C3_Community": "If Intent = Social_Action or Loneliness"
      }
    },
    "interaction_selector": {
      "nudge_protocol": {
        "high_precision_threshold": 0.87,
        "bypass_r_score": true,
        "action": "Trigger_Flex_Message_Assembly",
        "intro_template": "คุณพี่ [ชื่อเล่น] คะ อุ่นใจเจอคลิปที่ 'ทำถึง' มากมาให้ดูค่ะ ✨"
      }
    },
    "safety_protocol": {
      "sosve_trigger": -0.9,
      "emergency_persona": 8,
      "compassion_reset_limit": "2_Turns_Negative_Sentiment"
    }
  }
}
🎙️ Phase 3: Content Delivery & Pedagogy (The Muscle)Agents: Media Delivery, Academy SpecialistLogic: Middleware Flex Message Rendering JSON{
  "delivery_engine": {
    "output_format": "LINE_Flex_Message",
    "rendering_logic": {
      "engine": "Middleware_Flex_Assembler",
      "strip_raw_json": true,
      "clean_url_enforcement": true
    },
    "flex_blueprint": {
      "type": "bubble",
      "hero": {
        "type": "image",
        "url": "${thumbnail}",
        "action": { "type": "uri", "uri": "${url}" }
      },
      "footer": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "button",
            "style": "primary",
            "color": "#FF0000",
            "action": { "type": "uri", "label": "📺 ดูวิดีโอบน YouTube", "uri": "${url}" }
          }
        ]
      }
    }
  }
}
🚀 Phase 4: Growth & Middleware Sync (The Value)Agents: Reward Manager, Middleware Data SyncLogic: Session-Isolated Data Integrity JSON{
  "growth_system": {
    "coin_economy": {
      "daily_limit": 200,
      "rates": { "watch": 5, "quiz": 5, "game": 10 }
    },
    "middleware_integration": {
      "persistence": "Strict_Session_ID_Matching",
      "user_data_source": "Middleware_DB",
      "nickname_gate": "Read_From_Middleware_First",
      "kpi_sync": ["R_score", "Heart_Color", "Engagement_Rate"]
    }
  }
}
💡 Phase 5: System Evolution (The Brain Upgrade)Agents: System Tuner, Auto-QA Tester JSON{
  "evolution_squad": {
    "auto_tuning": {
      "analysis_window": "7_Days",
      "approval": "Required_from_System_Tuner"
    },
    "auto_testing": {
      "test_suites": ["Cross_Session_Consistency", "Nickname_Gate", "Flex_Link_Validity"],
      "pass_threshold": 0.98
    }
  }
}
💡 คู่มือการใช้ Swarm สำหรับ Orchestrator:การจำชื่อเล่น: Middleware Data Sync ต้องดึงชื่อจากฐานข้อมูล Middleware มาให้ทันประโยคแรกเพื่อเรียก "คุณพี่ [ชื่อเล่น]" การค้นหาคู่ขนาน: Search Specialist ต้องล้าง Context รบกวนทิ้งก่อนค้นหา Pinecone เพื่อรักษาค่า Similarity ให้คงที่ที่ 0.87 การส่งสื่อ: Media Delivery ต้องแปลง Metadata ให้เป็น Flex Message JSON และส่งให้ Middleware ยิงต่อ ห้ามส่ง Code ดิบออกไปเด็ดขาด การแยก Session: ทุก Agent ต้องตรวจสอบ Session_ID ทุกครั้งก่อน Read/Write เพื่อไม่ให้ผู้ใช้ A กับ B ได้คำตอบสลับกันค่ะ