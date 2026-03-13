# Agent Responsibility Refactor - AGENTS.md Squad 4 Compliance

## วันที่: 2026-03-13
## เป้าหมาย: แยก responsibility ระหว่าง Front-Desk และ Media Delivery Agent ให้ถูกต้อง

---

## ❌ Before (ไม่ถูกต้อง)

### Front-Desk Agent
```python
# Front-Desk สร้าง Flex Message เอง (ผิด!)
response = {
    "type": "flex",
    "flex_content": self._create_video_flex(video),  # ❌ ไม่ควรทำที่นี่
    ...
}
```

### Media Delivery Agent  
```python
# Media Delivery แค่ validate ของที่สร้างมาแล้ว (ผิด!)
flex_content = response.get("flex_content", {})  # ❌ ไม่ได้สร้างเอง
```

---

## ✅ After (ถูกต้องตาม AGENTS.md Squad 4)

### Front-Desk Agent (Squad 3: Front-Desk & Pedagogy)
**Responsibility:** ตัดสินใจว่าจะส่งอะไร (video หรือ text) + จัดเตรียมข้อมูล

```python
# Front-Desk คืน video METADATA เท่านั้น
response = {
    "type": "video",  # ✅ บอกว่าจะส่ง video
    "video_data": {   # ✅ ให้ข้อมูล video (ยังไม่สร้าง Flex)
        "title": video.get("title"),
        "full_url": video.get("full_url"),
        "thumbnail": video.get("thumbnail"),
        "score": video.get("score"),
        ...
    },
    "alt_text": "🎬 คลิปหนุนใจ",
    "metadata": {...}
}
```

### Media Delivery Agent (Squad 4: Content Integrity & Delivery)
**Responsibility:** สร้าง Flex Message และตรวจสอบความถูกต้องก่อนส่ง

```python
# Media Delivery รับ video_data แล้วสร้าง Flex Message
video_data = response.get("video_data", {})

# ✅ สร้าง Flex Message เองด้วย FlexMessageBuilder
if decision_type == "video_nudge":
    flex_content = FlexMessageBuilder.create_video_nudge(video_data)
else:
    flex_content = FlexMessageBuilder.create_video_card(video_data)

return {
    "status": "delivered",
    "type": "flex",
    "content": flex_content,  # ✅ Flex ที่สร้างเอง
    "alt_text": "...",
    "metadata": {...}
}
```

---

## 🏗️ Agent Workflow ที่ถูกต้อง

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Query                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1️⃣ Search Specialist (Squad 1)                                 │
│     - Hybrid Search (MEMORY.md + Pinecone)                      │
│     - Return: text_results + video_results                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2️⃣ Journey Architect (Squad 2)                                 │
│     - Analyze intent & R-score                                  │
│     - Decide: text_only / video_package / video_nudge           │
│     - Return: decision + selected_video                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3️⃣ Front-Desk (Squad 3)                                        │
│     - Decide response format                                    │
│     - Return: video METADATA (not built flex!)                  │
│     - Return: {"type": "video", "video_data": {...}}            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4️⃣ Media Delivery (Squad 4) ⭐ NEW                             │
│     - Build Flex Message from video_data                        │
│     - Use FlexMessageBuilder.create_video_card()                │
│     - Validate content integrity                                │
│     - Return: {"type": "flex", "content": {...}}                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  5️⃣ LINE Gateway                                                │
│     - Send Flex Message to user                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Agent Responsibilities Summary

| Agent | Squad | Responsibility | สิ่งที่ทำ |
|-------|-------|----------------|----------|
| **Search Specialist** | Squad 1 | Knowledge Retrieval | ค้นหาข้อมูลจาก MEMORY.md + Pinecone |
| **Journey Architect** | Squad 2 | Strategy & Routing | วิเคราะห์ intent, ตัดสินใจเลือก mode |
| **Front-Desk** | Squad 3 | Response Planning | จัดเตรียมข้อมูลที่จะส่ง (metadata) |
| **Media Delivery** | Squad 4 | **Content BUILDING** | **สร้าง Flex Message, ตรวจสอบเนื้อหา** |

---

## 🔧 Files Modified

1. **`docker/entrypoints/gateway_coordinated.py`**
   - Front-Desk: คืน `{"type": "video", "video_data": {...}}`
   - Media Delivery: สร้าง Flex Message ด้วย `FlexMessageBuilder`
   - ลบ `_create_video_flex()` และ `_create_nudge_flex()` ออกจาก class

2. **`modules/coordination_protocol.py`**
   - อัปเดต workflow ให้ส่ง video metadata ไป Media Delivery
   - ใช้ผลลัพธ์จาก Media Delivery เป็น final response

---

## ✅ AGENTS.md Squad 4 Compliance Checklist

- [x] Media Delivery Agent อยู่ใน Squad 4 (Content Integrity & Delivery)
- [x] Media Delivery สร้าง Flex Message (ไม่ใช่แค่ validate)
- [x] Front-Desk คืน metadata (ไม่สร้าง Flex)
- [x] ใช้ FlexMessageBuilder ใน Media Delivery
- [x] ตรวจสอบความถูกต้องของเนื้อหาก่อนส่ง
- [x] Workflow: Search → Architect → Front-Desk → **Media Delivery** → User

---

*Refactor completed: 2026-03-13 07:20 UTC*
