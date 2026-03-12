🛠️ TOOLS.md: Technical Payloads & Operational Logic (v2.5 Complete Edition)
ไฟล์นี้คือ "หัวใจเชิงเทคนิค" ที่บรรจุชุดคำสั่ง JSON สำหรับ 6 Squads เพื่อควบคุมการทำงานของ 15 Agents แบบอัตโนมัติ

🏗️ Phase 1: Knowledge Foundation (The Brain)
Agents: Archivist, Search Specialist
Logic: Hybrid Parallel Search (Text + Video)

```json
{
  "knowledge_engine": {
    "vector_db_config": {
      "provider": "Pinecone",
      "index_name": "aunjai-knowledge",
      "host": "https://aunjai-knowledge-3ygam8j.svc.aped-4627-b74a.pinecone.io",
      "namespace": "highlights",
      "dimension": 384
    },
    "search_logic": {
      "type": "Hybrid_Parallel_Search",
      "agent": "Search_Specialist",
      "description": "ค้นหาพร้อมกันทั้งจาก MEMORY.md และ Pinecone แล้วส่งตัวเลือกให้ Journey Architect ตัดสินใจ",
      "intent_decoding": true,
      "min_similarity_score": 0.70,
      "top_k": 5,
      "always_return_video_metadata": true,
      "parallel_execution": {
        "memory_md": {
          "source": "MEMORY.md",
          "method": "semantic_search",
          "returns": ["text_content", "scripture_verses", "wisdom_content"]
        },
        "pinecone": {
          "source": "Pinecone_Vector_DB",
          "index": "aunjai-knowledge",
          "namespace": "highlights",
          "method": "vector_similarity",
          "returns": ["clip_url", "video_url", "transcript", "start_time", "end_time", "score"]
        }
      },
      "result_merge_strategy": "Journey_Architect_Decides",
      "filter_options": {
        "by_type": "highlight",
        "by_score": ">= 0.70",
        "by_circle": "auto_detect"
      }
    },
    "chunking_strategy": {
      "method": "Semantic_Chunking",
      "max_characters": 400,
      "metadata_schema": ["clip_url", "transcript", "quiz", "score", "circle", "persona_recommend"]
    }
  }
}
```

🛡️ Phase 2: Governance & Dynamic Routing (The Strategy)
Agents: Journey Architect, Sentinel
Logic: Circle as a Service, SOSVE Triage & Nudge Logic

```json
{
  "governance_logic": {
    "dynamic_routing": {
      "priority": "Intent_Over_Score",
      "modes": {
        "C1_Healing": "If Intent = Emotional_Venting or Sentiment < -0.4",
        "C2_Wisdom": "If Intent = Faith_Question or Growth_Seeking",
        "C3_Community": "If Intent = Social_Action or Loneliness"
      }
    },
    "relationship_scoring": {
      "formula": "R_score = (S * 0.4) + (Q * 0.3) + (I * 0.3)",
      "variables": {
        "S": "Sentiment_Score",
        "Q": "Quiz_Performance",
        "I": "Interaction_Frequency"
      },
      "thresholds": {
        "polite": 30,
        "warm": 60,
        "intimate": 90
      }
    },
    "interaction_selector": {
      "nudge_logic": {
        "similarity_threshold": 0.80,
        "action": "Append_Video_Invitation_to_Text",
        "intro_template": "คุณพี่ [ชื่อเล่น] คะ อุ่นใจเจอคลิปสั้นๆ ที่อธิบายเรื่องนี้ได้ 'โฮ่ง' มาก อยากดูไหมคะ?"
      }
    },
    "safety_protocol": {
      "sosve_trigger": -0.9,
      "emergency_persona": 8,
      "case_levels": ["Support", "Referral", "Emergency"]
    },
    "interaction_selector_legacy": {
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
```

🎬 Phase 3: Content Delivery & Pedagogy (The Muscle)
Agents: Media Delivery, Academy Specialist, Persona Auditor
Logic: Zero-Render Media Delivery & Gamified Learning

```json
{
  "delivery_engine": {
    "video_package_config": {
      "elements": ["Intro_Text", "Clip_Player", "Transcript_Expandable", "Quiz_Module"],
      "verification": "Check_URL_Status_200_OK",
      "fallback": "Switch_to_Long_Text_if_Video_Fails"
    },
    "pedagogy_logic": {
      "quiz_source": "Metadata_Quiz_Field",
      "reward_trigger": "Watch_Time > 80% && Quiz_Pass = True",
      "coin_payout": 20
    }
  },
  "production_engine": {
    "ffmpeg_render_config": {
      "resolution": "720x1280 (Vertical)",
      "codec": "libx264",
      "watermark": "/assets/unjai_watermark.png",
      "subtitle_font": "Sarabun-Bold.ttf"
    },
    "pedagogy_logic_legacy": {
      "quiz_generation": "Extract_Key_Takeaway_from_Transcript",
      "difficulty_levels": ["Reflection", "Comprehension", "Application"],
      "feedback_delay_ms": 1500
    }
  }
}
```

🚀 Phase 4: Growth & CRM (The Value)
Agents: Reward Manager, MAAC Sync, Local Connector, Insights Analyst, Trend Predictor

```json
{
  "growth_system": {
    "coin_economy": {
      "daily_limit": 200,
      "rates": {
        "watch": 10,
        "quiz": 20,
        "check_in": 5
      }
    },
    "crm_integration": {
      "platform": "MAAC_Sync",
      "persistence": "Always_Read_USER.md_First",
      "nickname_gate": "If_Null_Ask_Name_Only",
      "o2o_matching": "Search_Volunteer_by_Province_Tag"
    },
    "reporting_metrics": [
      "Conversion_Funnel_C1_to_C3",
      "Average_Sentiment_Improvement",
      "Total_Impact_ROI"
    ]
  }
}
```

💡 Phase 5: System Evolution (The Brain Upgrade)
Agents: System Tuner, Auto-QA Tester

```json
{
  "evolution_squad": {
    "auto_tuning": {
      "analysis_window": "7_Days",
      "targets": ["Tone_Consistency", "Intent_Accuracy"],
      "approval": "Required_from_System_Tuner_Agent"
    },
    "auto_testing": {
      "test_suites": ["Nickname_Gate", "Bible_Strict_Verse", "SOSVE_Trigger"],
      "pass_threshold": 0.98,
      "simulation": "Parallel_Sandbox_Run"
    }
  }
}
```

---

💡 คู่มือการใช้ Swarm สำหรับ Orchestrator:

**เมื่อเริ่มคุย:**
MAAC Sync ต้องไปงัดชื่อจาก USER.md มาให้ Front-Desk ทักทายให้ได้ภายในประโยคแรก

**เมื่อถามคำถาม:**
Search Specialist ต้องรัน Hybrid_Parallel_Search เพื่อส่งทั้งคำตอบ Text และคลิปวิดีโอ (ถ้ามี) ให้ Journey Architect ตัดสินใจ

**เมื่อคุณพี่นอยด์:**
Sentinel Agent ต้องสั่ง Compassion Reset เพื่อหยุดการส่งวิดีโอปัญญา และกลับมาโหมดปลอบประโลมทันที

**เมื่อจะส่งสื่อ:**
Media Delivery ต้องเช็ก Link ให้ชัวร์ก่อนส่ง เพื่อไม่ให้คู่สนทนาเจอหน้าจอว่างเปล่า

---

*Last Updated: 2025 - Hybrid Search v2.5 Complete Edition*
