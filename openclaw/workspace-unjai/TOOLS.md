TOOLS.md: Technical Payloads & Operational Logic (Phase 1-4)
ไฟล์นี้บรรจุชุดคำสั่ง JSON และพารามิเตอร์เชิงเทคนิคสำหรับระบบ Swarm เพื่อขับเคลื่อนกิจกรรมในทุกเฟส

🏗️ Phase 1: Knowledge Foundation (The Brain)
Agents: Archivist, Search Specialist

JSON
{
  "knowledge_engine": {
    "chunking_strategy": {
      "method": "Semantic_Chunking",
      "max_characters": 400,
      "overlap": 50,
      "metadata": ["video_id", "timestamp", "circle_tag"]
    },
    "search_logic": {
      "type": "FAISS_Vector_Search",
      "index_path": "/data/vector_db/unjai_main",
      "intent_decoding": true,
      "min_similarity_score": 0.75
    }
  }
}
🛡️ Phase 2: Governance & Safety (The Strategy)
Agents: Journey Architect, Sentinel

JSON
{
  "governance_logic": {
    "relationship_scoring": {
      "formula": "R_score = (S * 0.4) + (Q * 0.3) + (I * 0.3)",
      "variables": {
        "S": "Sentiment_Score",
        "Q": "Quiz_Performance",
        "I": "Interaction_Frequency"
      }
    },
    "safety_monitoring": {
      "sos_trigger_level": -0.9,
      "persona_8_override": true,
      "alert_protocol": "Notify_Human_Volunteer_Immediate"
    },
    "interaction_selector": {
      "description": "3-Filter System สำหรับตัดสินใจเลือกรูปแบบการตอบ (Text vs Video)",
      "filters": {
        "filter_1_content_depth": {
          "text_conditions": ["Fact_Check_Query", "Short_Answer_Needed", "R_score < 30"],
          "video_conditions": ["High_Emotional_Intensity", "Testimony_Related", "Sentiment_Based_Query"]
        },
        "filter_2_r_score_threshold": {
          "text_only": "R_score < 30 (New User - Build Trust First)",
          "video_nudge": "R_score 30-60 (Warm User - Transition to Circle 2)",
          "full_package": "R_score > 60 (Circle 2 - Video + Transcript + Quiz)"
        },
        "filter_3_interest_match": {
          "highlight_clips": "หากคำถามตรงกับ Highlight Clip ที่คัดไว้ว่า 'โฮ่งที่สุด' ส่งวิดีโอทันทีเพื่อสร้าง First Impression"
        }
      },
      "mode_switch": {
        "priority": "Sentiment_First",
        "text_only_conditions": ["Low_Rscore", "Fact_Check_Query"],
        "video_package_conditions": ["High_Emotional_Intensity", "Interest_Match_Highlight"],
        "quiz_trigger": "Only_After_Video_Watch_80_Percent"
      },
      "response_patterns": {
        "text_only": "ตอบคำถามด้วยข้อมูลจาก MEMORY.md + ถามต่อเพื่อสานสัมพันธ์",
        "video_package": "ตอบก่อน (Intro Text) → ส่งวิดีโอ Highlight → ชวนทำ Quiz → แจกเหรียญ"
      }
    }
  }
}
🎬 Phase 3: Production & Pedagogy (The Muscle)
Agents: FFmpeg Director, Academy Specialist, QA Validator

JSON
{
  "production_engine": {
    "ffmpeg_render_config": {
      "resolution": "720x1280 (Vertical)",
      "codec": "libx264",
      "watermark": "/assets/unjai_watermark.png",
      "subtitle_font": "Sarabun-Bold.ttf"
    },
    "pedagogy_logic": {
      "quiz_generation": "Extract_Key_Takeaway_from_Transcript",
      "difficulty_levels": ["Reflection", "Comprehension", "Application"],
      "feedback_delay_ms": 1500
    }
  }
}
📈 Phase 4: Growth & Intelligence (The Value)
Agents: Reward Manager, MAAC Sync, Insights Analyst

JSON
{
  "growth_system": {
    "coin_economy": {
      "daily_limit": 200,
      "rates": {
        "watch_video": 10,
        "complete_quiz": 20,
        "share_content": 15
      }
    },
    "crm_integration": {
      "platform": "MAAC_Sync",
      "tag_logic": "Update_User_Persona_Tag_Daily",
      "location_matching": "Search_Volunteer_Radius_50km"
    },
    "reporting_metrics": [
      "Conversion_Funnel_C1_to_C3",
      "Average_Sentiment_Improvement",
      "Total_Impact_ROI"
    ]
  }
}
💡 วิธีใช้งานสำหรับ Swarm:
เมื่อ Archivist จะทำ Chunking: ให้มาดึงค่า max_characters จาก Phase 1 ในไฟล์นี้

เมื่อ FFmpeg จะเรนเดอร์วิดีโอ: ให้มาดึงค่า resolution และ codec จาก Phase 3 ในไฟล์นี้

เมื่อ Reward Manager จะจ่ายเหรียญ: ให้เช็ก rates จาก Phase 4 ในไฟล์นี้
{
  "evolution_squad": {
    "auto_tuning": {
      "analysis_window_days": 7,
      "optimization_targets": ["Tone_Consistency", "Slang_Accuracy"],
      "approval_required": true
    },
    "auto_testing": {
      "test_suites": ["Identity_Check", "Bible_Accuracy", "Safety_Trigger"],
      "pass_threshold": 0.95,
      "simulation_mode": "Parallel_Sandbox"
    }
  }
}