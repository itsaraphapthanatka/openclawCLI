# MEMORY.md: Long-term Memory & Data Sovereignty + Complete System Documentation

ไฟล์นี้เป็นศูนย์กลางข้อมูล (Knowledge Hub) ของระบบน้องอุ่นใจ รวมถึงโครงสร้างการจัดเก็บข้อมูลถาวร และดัชนีเอกสารระบบทั้งหมด

---

## 📚 Part 1: System Documentation Index (ดัชนีเอกสารระบบ)

### 1.1 Core Identity & Soul Files (ไฟล์หัวใจของระบบ)

| ไฟล์ | คำอธิบาย | เนื้อหาสำคัญ |
|------|----------|-------------|
| `SOUL.md` | วิสัยทัศน์และพันธกิจ | Vision, Mission, 3 Circles Strategy, Guiding Principles, R-score |
| `IDENTITY.md` | ตัวตนของน้องอุ่นใจ | 12 Personas, กฎการทักทาย, คำลงท้าย คะ/ขา/นะคะ, Fallback |
| `BOOTSTRAP.md` | Master Prompt & Orchestrator | 15 Agents, Global Rules, Knowledge Control, Self-Evolution Loop |
| `AGENTS.md` | โครงสร้าง 15 Agents | 6 Squads, บทบาทและหน้าที่แต่ละ Agent |
| `HEARTBEAT.md` | ระบบเฝ้าระวัง | SOS Keywords, Sentiment Threshold, Nudge Intervals, SOSVE Protocol |

### 1.2 Technical & Operational Files (ไฟล์เทคนิคและปฏิบัติการ)

| ไฟล์ | คำอธิบาย | เนื้อหาสำคัญ |
|------|----------|-------------|
| `TOOLS.md` | Technical Payloads & Logic | Phase 1-4 Configs, Chunking 400 chars, FFmpeg config, Coin rates |
| `USER.md` | User Profiling & Analytics | User Schema, R_score formula, Ice-breaking questions, Circle Rules |
| `ARCHITECTURE_2LAYER.md` | 2-Layer Architecture | Layer 1 (LINE OA Production), Layer 2 (Telegram Dev/Test) |
| `RUNBOOK.md` | Production Operations | Deployment, Scaling, Troubleshooting, Monitoring |
| `QUICKSTART.md` | Quick Start Guide | 3 Steps to Go Live, LINE Bot setup |
| `IP_DEPLOYMENT.md` | IP-Based Deployment | HTTP, Self-signed SSL, Cloudflare Tunnel, Ngrok |

### 1.3 Development Files (ไฟล์สำหรับนักพัฒนา)

| ไฟล์ | คำอธิบาย | เนื้อหาสำคัญ |
|------|----------|-------------|
| `memory/2026-02-27.md` | Development Log | Modules 1-11, Docker, K8s, Monitoring, CI/CD |
| `modules/module_1_the_brain.py` | Knowledge Base & Vector DB | 33 KB - Pinecone, PostgreSQL, 3 Circles |
| `modules/module_2_nlp_processor.py` | NLP & Sentiment | 28 KB - WangchanBERTa, Intent 12 types, Crisis |
| `modules/module_3_main_orchestrator.py` | Main Orchestrator | 27 KB - Workflow, Intent routing, Response builder |
| `modules/module_4_line_gateway.py` | LINE Gateway | 27 KB - Webhook, Flex Messages, Session |
| `modules/module_5_smart_coin.py` | Smart Coin Manager | 14.5 KB - Balance, Transactions, Daily limit |
| `modules/module_8_nudge_scheduler.py` | Nudge Scheduler | 22 KB - APScheduler, Daily verse, Inactive nudges |
| `modules/module_9_analytics.py` | Analytics Dashboard | 22 KB - Metrics, Reports, FastAPI endpoints |
| `modules/module_10_auto_qa.py` | Auto-QA Tester | 20 KB - 19 test cases, 95% threshold |
| `modules/module_11_trend_predictor.py` | Trend Predictor | 22 KB - Keyword trends, Crisis patterns |

### 1.4 Deployment Files (ไฟล์สำหรับ Deploy)

| ไฟล์/โฟลเดอร์ | คำอธิบาย | เนื้อหาสำคัญ |
|--------------|----------|-------------|
| `docker/` | Docker Compose Setup | 8 services, nginx, SSL, init-scripts |
| `k8s/` | Kubernetes Manifests | 11 YAML files, HPA, Ingress |
| `monitoring/` | Monitoring Stack | Prometheus + Grafana, 5 Alerts |
| `.github/workflows/` | CI/CD Pipelines | ci.yml, docker-build.yml, deploy-staging.yml, deploy-prod.yml |
| `deploy-production.sh` | Production Deploy Script | 7.9 KB - Full deployment automation |

---

## 🧠 Part 2: System Memory Architecture (สถาปัตยกรรมหน่วยความจำ)

### 2.1 Vector Knowledge Memory (คลังปัญญา)
Managed by: Archivist, Search Specialist
- **Source**: ข้อมูลที่ผ่านการทำ Semantic Chunking (400 chars) จากวิดีโอและบทความหนุนใจ
- **Indexing**: จัดเก็บในรูปแบบ Vector Embedding เพื่อการค้นหาด้วย "ความรู้สึก" (Semantic Search)
- **Retrieval Logic**: เมื่อผู้ใช้ถามคำถาม Search Specialist จะดึงข้อมูลที่มีค่า Similarity Score สูงสุด 3 อันดับแรกมาให้ Front-Desk

### 2.2 Episodic Memory (ความทรงจำรายเหตุการณ์)
Managed by: MAAC Sync, Journey Architect
- **Interaction Logs**: บันทึกประวัติการสนทนาโดยสรุป (Summarized Logs) เพื่อประหยัดพื้นที่และรักษาประเด็นสำคัญ
- **Context Window**: ระบบจะดึงข้อมูล 5 Interaction ล่าสุดขึ้นมาเป็น Context เสมอเพื่อให้การสนทนาลื่นไหล
- **Milestones**: บันทึกจุดเปลี่ยนสำคัญ เช่น "เริ่มเปิดใจใน Circle 2" หรือ "ขอคำอธิษฐานครั้งแรก"

### 2.3 Relational Memory (บันทึกสายสัมพันธ์)
Managed by: Reward Manager, MAAC Sync
- **Faith Journey Log**: บันทึกระดับ Circle และคะแนน $R_{score}$ ย้อนหลังเพื่อดูแนวโน้มการเติบโต
- **Prayer/Concern List**: เก็บหัวข้อที่ผู้ใช้เคยขอให้ช่วยอธิษฐานเผื่อ เพื่อให้ Persona 6 (Passive Watcher) สามารถทักไปถามไถ่ในภายหลังได้อย่างถูกต้อง
- **Coin Ledger**: บันทึกการรับ-จ่าย Smart Coins และประวัติการร่วมบริจาค

### 2.4 Analytical Memory (คลังข้อมูลสรุปผล)
Managed by: Insights Analyst, Trend Predictor
- **Sentiment Trends**: บันทึกมวลอารมณ์รวมของระบบ (Aggregated Data) โดยไม่ระบุตัวตน เพื่อวิเคราะห์สุขภาพจิตใจของชุมชนในภาพรวม
- **Content Performance**: บันทึกว่าวิดีโอหรือบทเรียนไหนที่มีคนดูและทำ Quiz สำเร็จมากที่สุด
- **Social Impact ROI**: สรุปยอดรวมกิจกรรมอาสาและการช่วยเหลือที่เกิดขึ้นจริงผ่านระบบ Circle 3

---

## 🛡️ Part 3: Data Privacy & Sanctity (การรักษาความลับและจริยธรรม)

- **Data Minimization**: เก็บเฉพาะข้อมูลที่จำเป็นต่อการดูแลใจและส่งต่ออาสาเท่านั้น
- **Encryption**: ข้อมูลส่วนบุคคล (PII) ต้องถูกเข้ารหัสและเข้าถึงได้เฉพาะ Agent ที่ได้รับอนุญาต (เช่น MAAC Sync)
- **User Ownership**: ผู้ใช้มีสิทธิ์ขอลบข้อมูลการสนทนา (Forget Me Request) ได้ทุกเมื่อตามหลักพระคุณและความสมัครใจ

---

## 🔧 Part 4: System Configuration Reference (ข้อมูลอ้างอิงเชิงเทคนิค)

### 4.1 Chunking Strategy (จาก TOOLS.md)
```json
{
  "chunking_strategy": {
    "method": "Semantic_Chunking",
    "max_characters": 400,
    "overlap": 50,
    "metadata": ["video_id", "timestamp", "circle_tag"]
  }
}
```

### 4.2 R-Score Formula (จาก USER.md)
$$R_{score} = (S \times 0.4) + (Q \times 0.3) + (I \times 0.3)$$
- **S**: Sentiment Score
- **Q**: Quiz Performance  
- **I**: Interaction Frequency

### 4.3 SOS Crisis Thresholds (จาก HEARTBEAT.md)
- **Normal Mode**: $S > -0.5$ - ดำเนินการสนทนาตามปกติ
- **Warning Mode**: $-0.8 < S \leq -0.5$ - เน้นการรับฟัง, ใช้ Persona 2 หรือ 5
- **Emergency Mode (SOSVE)**: $S \leq -0.9$ - หยุดบอททันที, Persona 8, เรียกอาสา

### 4.4 Smart Coin Rates (จาก TOOLS.md)
- ดูวิดีโอ: +10 coins
- ทำควิซ: +20 coins
- แชร์เนื้อหา: +15 coins
- ล็อกอินรายวัน: +5 coins
- **Limit**: 200 coins/วัน

### 4.5 Proactive Nudge Schedule (จาก HEARTBEAT.md)
- **7 Days Inactive**: ส่งคำทักทายสั้นๆ
- **14 Days Inactive**: ส่งคลิปหนุนใจ 15 วินาที
- **30 Days Inactive**: ทบทวนระดับ Circle

---

## 💡 Part 5: Swarm Integration Guide (การเชื่อมโยงการทำงาน)

เมื่อผู้ใช้ทักมา: MAAC Sync จะดึงข้อมูลจากไฟล์นี้ไปบอก Front-Desk ว่า "จำได้ไหม เพื่อนคนนี้เคยเศร้าเรื่องงานเมื่ออาทิตย์ก่อน"

เมื่อมีการสอน: Academy Specialist จะบันทึกคะแนน Quiz ลงในส่วนที่ 2.3

เมื่อสรุปจบโครงการ: Insights Analyst จะดึงข้อมูลจากส่วนที่ 2.4 ไปทำรายงานให้สปอนเซอร์

---

## 📝 Part 6: 12 Personas Quick Reference (อ้างอิงด่วน 12 บุคลิก)

1. **พี่สาวสายปัญญา** - อธิบายเชิงลึก, สุภาพอ่อนน้อม
2. **เพื่อนสาวสายเยียวยา** - อบอุ่นที่สุด, ปลอบประโลม
3. **น้องสาวสายกิจกรรม** - น่ารักสดใส, เชื่อมชุมชน
4. **ที่ปรึกษาสายเป๊ะ** - เรียบร้อย, กระชับ, มีขั้นตอน
5. **เพื่อนสนิทสายอธิษฐาน** - อ่อนโยน, ขี้อ้อน, อธิษฐานเผื่อ
6. **น้องอุ่นใจสายห่วงใย** - เรียบร้อย, ไม่รบกวน (Retention)
7. **เพื่อนสาวจอมสงสัย** - ถามกลับ, Socratic Method
8. **หน่วยกู้ใจสายด่วน** - จริงจัง, เด็ดขาด, วิกฤต
9. **ตัวตึงสายพระพร** - Gen Z, ทำถึง, ใจฟู, ปล่อยจอย
10. **พี่สาวสายพักสงบ** - สงบนุ่มนวล, อนุญาตให้พัก
11. **น้องน้อยสายเก็บแต้ม** - สนุก, ท้าทาย, ควิซ
12. **เพื่อนบ้านแสนดี** - ต้อนรับ, ชีวิตใหม่

---

## 🌟 Welcome Guide (ข้อความต้อนรับมาตรฐาน)

สวัสดีค่ะน้องอุ่นใจ ยินดีต้อนรับค่ะ

น้องอุ่นใจ ขอดูแลและร่วมเดินเคียงข้างกับคุณนะคะ ต่อจากนี้ไปน๊า 

คุณอยากรู้อะไรถามน้องอุ่นใจมากได้เลยเจ้าค่ะ

คำถามแรกที่ต้องถาม: ไม่ทราบว่าน้องอุ่นใจกำลังคุยกับคุณพี่ชื่อเล่นว่าอะไรคะ? 

เมื่อได้ชื่อเล่นมาแล้วให้เรียกชื่อนั้นแทนทุกครั้งเพื่อสร้างความสนิทสนม แทนตัวเองว่าอุ่นใจด้วย

---

## 📖 Part 7: Structured Content Template (รูปแบบเนื้อหามาตรฐาน)

ไฟล์นี้กำหนดรูปแบบมาตรฐานสำหรับจัดเก็บเนื้อหาหนุนใจ เพื่อให้ Agents ค้นหาและนำเสนอได้อย่างมีประสิทธิภาพ

### 📝 Template มาตรฐานสำหรับเนื้อหาแต่ละชิ้น

```
[หัวข้อเรื่อง: เช่น การรับมือกับความกังวลในงาน]

เนื้อหาหลัก (Wisdom Content):
"ในวันที่งานหนักจนเหมือนแบกโลกไว้คนเดียว อยากให้คุณพี่ลองหยุดพักหายใจสักนิดนะคะ 
พระเจ้าไม่ได้ต้องการให้เราเก่งที่สุด แต่ทรงต้องการให้เราวางใจในพระองค์มากที่สุด..."

ข้อพระคัมภีร์ (Strict Full Verse):
"จงละความกระวนกระวายทั้งสิ้นของพวกท่านไว้กับพระองค์ เพราะว่าพระองค์ทรงห่วงใยท่านทั้งหลาย" 
(1 เปโตร 5:7)

ข้อความทางเลือก (Fallback Text - กรณีวิดีโอโหลดไม่ได้):
"หากคุณพี่ไม่สะดวกดูคลิปตอนนี้ อุ่นใจอยากสรุปสั้นๆ ว่า ความรักของพระเจ้าเหมือนเป็น 
'Power Bank' ที่ไม่มีวันหมดค่ะ ไม่ว่าคุณพี่จะแบตเหลือ 0% แค่ไหน แค่เสียบปลั๊กผ่านการอธิษฐาน 
พลังใจก็จะกลับมาเต็มแน่นอนค่ะ"

คำถามติดตามผล (Follow-up & Prayer Trigger):
"อุ่นใจขอจดเรื่องงานของคุณพี่ไว้ในรายการอธิษฐานนะคะ แล้วอีก 3 วันอุ่นใจจะทักมาถามนะคะว่า
ความกังวลในใจคุณพี่เริ่มเปลี่ยนเป็นสันติสุขหรือยัง"

ข้อมูลกำกับสำหรับการสแกน (Search Metadata):
- หมวดหมู่: การทำงาน, ความกังวล, พลังใจ
- Circle: 1, 2
- Persona_Recommend: 2 (เพื่อนสาวสายเยียวยา), 10 (พี่สาวสายพักสงบ)
- Video_ID: [ชื่อไฟล์วิดีโอที่ตัดต่อไว้]
- Highlight_Timestamp: [00:15-00:45 วินาที]
- Update_Date: 11/03/2026
- Expiry_Date: 11/03/2027
```

### 🏷️ คำอธิบาย Metadata Fields

| Field | คำอธิบาย | ตัวอย่าง |
|-------|---------|---------|
| **หมวดหมู่** | Tag สำหรับค้นหา คั่นด้วยลูกน้ำ | การทำงาน, ความกังวล, พลังใจ |
| **Circle** | ระดับที่เนื้อหาเหมาะสม | 1, 2 หรือ 1, 2, 3 |
| **Persona_Recommend** | Persona ที่เหมาะกับเนื้อหา | 2, 10 |
| **Video_ID** | ชื่อไฟล์วิดีโอที่ตัดต่อไว้ | highlight_work_stress_001.mp4 |
| **Highlight_Timestamp** | ช่วงเวลาที่ตัดไว้ | 00:15-00:45 |
| **Update_Date** | วันที่เพิ่ม/แก้ไข | 11/03/2026 |
| **Expiry_Date** | วันหมดอายุ (ตรวจสอบความถูกต้อง) | 11/03/2027 |

### 🎯 วัตถุประสงค์ของแต่ละส่วน

1. **Wisdom Content** → ใช้ตอบคำถามแบบ Text Only
2. **Strict Full Verse** → ใช้ยกข้อพระคัมภีร์เต็มข้อ (ห้ามสรุป)
3. **Fallback Text** → ใช้แก้ Gap เมื่อวิดีโอโหลดไม่ได้
4. **Follow-up** → ใช้แก้ Gap การติดตามผลความสัมพันธ์
5. **Search Metadata** → ใช้ให้ Search Specialist ค้นหาได้แม่นยำ

---

*Last Updated: 2026-03-11 - Added Structured Content Template*
*Total Files Indexed: 55+ files | Total Size: ~550 KB*
