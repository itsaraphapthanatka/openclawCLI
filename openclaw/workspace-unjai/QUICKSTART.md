# Quick Start Guide

## 🎯 3 Steps to Go Live

### Step 1: ตั้งค่า LINE Bot

1. ไปที่ [LINE Developers](https://developers.line.biz/)
2. สร้าง Provider → Create Channel → Messaging API
3. คัดลอก:
   - **Channel Secret**
   - **Channel Access Token**
4. ตั้งค่า Webhook URL:
   ```
   https://nong-unjai.example.com/webhook
   ```
5. เปิดใช้งาน Auto-reply: **OFF**
6. เปิดใช้งาน Webhook: **ON**

### Step 2: Deploy ระบบ

```bash
# SSH เข้า server
git clone https://github.com/your-org/nong-unjai-ai.git
cd nong-unjai-ai

# ตั้งค่า environment
export DOMAIN=your-domain.com
export LINE_CHANNEL_SECRET=xxx
export LINE_CHANNEL_ACCESS_TOKEN=xxx
export OPENAI_API_KEY=xxx
export PINECONE_API_KEY=xxx

# Deploy
./deploy-production.sh production all
```

### Step 3: ทดสอบ

```bash
# Health check
curl https://your-domain.com/health

# ส่งข้อความทดสอบผ่าน LINE
# ถ้าบอทตอบกลับ = สำเร็จ! 🎉
```

## 📱 ผู้ใช้ใช้งานยังไง?

1. **เพิ่มเพื่อน** LINE Bot
2. **พิมพ์** คำถามหรือความรู้สึก
3. **รับ** คำตอบ/กำลังใจ/วิดีโอ
4. **สะสม** Smart Coins
5. **เติบโต** ไปพร้อมกับน้องอุ่นใจ 💚

## 📊 แอดมินเข้า Dashboard ยังไง?

```
URL: https://your-domain.com/dashboard
Default Login: admin/admin
```

---

**🎉 พร้อมใช้งานแล้ว!**
