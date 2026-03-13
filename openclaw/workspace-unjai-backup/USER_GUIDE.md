# Nong Unjai AI - คู่มือการใช้งาน

## 👋 สำหรับผู้ใช้ทั่วไป (ผ่าน LINE)

### เริ่มต้นใช้งาน

1. **เพิ่มเพื่อน** กับ Nong Unjai AI บน LINE
2. **ส่งข้อความ** ทักทายครั้งแรก
3. **บอกชื่อเล่น** ให้น้องอุ่นใจจำได้

```
คุณ: สวัสดี
อุ่นใจ: สวัสดีค่ะ! ไม่ทราบว่าน้องอุ่นใจกำลังคุยกับคุณพี่ชื่อเล่นว่าอะไรคะ?

คุณ: ต้น
อุ่นใจ: ยินดีที่ได้รู้จักค่ะคุณพี่ต้น! 🥰
```

### คำสั่งที่ใช้ได้

#### 1. ถามคำถามเกี่ยวกับพระคัมภีร์
```
คุณ: ยอห์น 3:16 ว่าอะไร
อุ่นใจ: "พระเจ้าทรงรักโลกถึงกับทรงประทานพระบุตร..." 💚
```

#### 2. ขอกำลังใจ
```
คุณ: วันนี้เหนื่อยมาก
อุ่นใจ: คุณพี่ต้น อุ่นใจเข้าใจค่ะ... ข้อพระคัมภีร์นี้ฮีลใจนะคะ 💕
```

#### 3. ดูวิดีโอหนุนใจ
```
คุณ: อยากดูคลิป
อุ่นใจ: นี่ค่ะคลิปสำหรับคุณพี่ต้น... 🎬
[ส่งวิดีโอ Flex Message]
```

#### 4. ทำควิซ
```
คุณ: ทำแบบทดสอบ
อุ่นใจ: มาเลยค่ะ! คำถามแรก...
[ส่ง Quiz Flex Message]
```

#### 5. เช็คเหรียญ
```
คุณ: เช็คเหรียญ
อุ่นใจ: คุณพี่ต้นมี 150 Smart Coins ค่ะ 🪙
```

#### 6. ขอให้อธิษฐานเผื่อ
```
คุณ: ช่วยอธิษฐานเผื่อด้วย
อุ่นใจ: ได้ค่ะคุณพี่ต้น อุ่นใจจะอธิษฐานเผื่อคุณพี่นะคะ 🙏
```

### การได้รับเหรียญ 🪙

| กิจกรรม | เหรียญที่ได้ |
|---------|-------------|
| ดูวิดีโอ | +10 |
| ทำควิซ | +20 |
| แชร์เนื้อหา | +15 |
| เข้าสู่ระบบรายวัน | +5 |
| สตรีก 7 วัน | +50 |

---

## 👨‍💼 สำหรับแอดมิน

### เข้า Dashboard

```
URL: https://nong-unjai.example.com/dashboard
Username: admin
Password: (ตั้งค่าใน docker/.env)
```

### หน้าต่างๆ ใน Dashboard

#### 1. 📊 Overview
- จำนวนผู้ใช้ทั้งหมด
- ผู้ใช้ที่กำลังใช้งาน
- ข้อความต่อวัน
- อัตราการตอบกลับ

#### 2. 💚 R-Score Distribution
- กราฟการกระจายคะแนนสุขภาพจิต
- ผู้ใช้ที่ต้องการดูแลเป็นพิเศษ

#### 3. 🚨 Crisis Reports
- เหตุการณ์วิกฤตย้อนหลัง
- เวลาตอบสนอง
- สถานะการช่วยเหลือ

#### 4. 🎬 Content Performance
- วิดีโอยอดนิยม
- ควิซที่ทำบ่อย
- คะแนนเฉลี่ย

#### 5. 🪙 Coin Economy
- ยอดเหรียญในระบบ
- การจ่าย/รับเหรียญ
- ยอดบริจาค

---

## 🔌 API Reference

### Health Check
```bash
GET https://nong-unjai.example.com/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "gateway": "up",
    "orchestrator": "up",
    "database": "up"
  }
}
```

### Send Message (Webhook)
```bash
POST https://nong-unjai.example.com/webhook
Content-Type: application/json
X-Line-Signature: {signature}

{
  "events": [{
    "type": "message",
    "message": {
      "type": "text",
      "text": "สวัสดี"
    },
    "source": {
      "userId": "U123456789"
    }
  }]
}
```

### Analytics API

#### Get Dashboard Data
```bash
GET https://nong-unjai.example.com/dashboard
```

#### Get Engagement Metrics
```bash
GET https://nong-unjai.example.com/metrics/engagement?period=week
```

#### Get Sentiment Analysis
```bash
GET https://nong-unjai.example.com/metrics/sentiment?period=month
```

#### Get Crisis Reports
```bash
GET https://nong-unjai.example.com/metrics/crisis?period=today
```

#### Get R-Score Distribution
```bash
GET https://nong-unjai.example.com/metrics/rscore
```

#### Get ROI Report
```bash
GET https://nong-unjai.example.com/reports/roi?period=quarter
```

---

## 🛠️ สำหรับนักพัฒนา

### Clone และรันบนเครื่อง

```bash
# 1. Clone
git clone https://github.com/your-org/nong-unjai-ai.git
cd nong-unjai-ai

# 2. สร้าง virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. ติดตั้ง dependencies
pip install -r requirements.txt

# 4. ตั้งค่า environment
export LINE_CHANNEL_SECRET=xxx
export LINE_CHANNEL_ACCESS_TOKEN=xxx
export OPENAI_API_KEY=xxx
export POSTGRES_PASSWORD=xxx
export REDIS_PASSWORD=xxx

# 5. รันโมดูลที่ต้องการ
cd modules
python module_4_line_gateway.py
```

### โครงสร้างโปรเจค

```
nong-unjai-ai/
├── modules/              # โค้ด Python ทั้งหมด
│   ├── module_1_the_brain.py
│   ├── module_2_nlp_processor.py
│   ├── module_3_main_orchestrator.py
│   ├── module_4_line_gateway.py
│   ├── module_5_smart_coin.py
│   ├── module_8_nudge_scheduler.py
│   ├── module_9_analytics.py
│   ├── module_10_auto_qa.py
│   └── module_11_trend_predictor.py
├── docker/               # Docker & Docker Compose
├── k8s/                  # Kubernetes manifests
├── monitoring/           # Prometheus & Grafana
├── .github/workflows/    # CI/CD pipelines
└── tests/                # Unit tests
```

---

## 🆘 แก้ไขปัญหา

### บอทไม่ตอบกลับ

1. เช็ค health endpoint:
```bash
curl https://nong-unjai.example.com/health
```

2. เช็ค logs:
```bash
kubectl logs -f deployment/gateway -n unjai
```

3. รีสตาร์ท service:
```bash
kubectl rollout restart deployment/gateway -n unjai
```

### Database connection error

```bash
# เช็ค postgres
kubectl get pods -n unjai | grep postgres

# Restart postgres
kubectl delete pod postgres-0 -n unjai
```

### SSL certificate expired

```bash
cd docker/ssl
./renew-cert.sh
```

---

## 📞 ติดต่อสนับสนุน

- **Email**: support@nong-unjai.example.com
- **LINE**: @nongaunjai
- **Documentation**: https://docs.nong-unjai.example.com

---

## 🎓 Tips & Tricks

### สำหรับผู้ใช้
- 💡 พิมพ์ "ช่วยด้วย" หากต้องการติดต่ออาสาสมัครจริง
- 💡 น้องอุ่นใจจะทักทายอัตโนมัติทุกเช้า 8 โมง
- 💡 สะสมสตรีกเข้าสู่ระบบ 7 วันติดต่อกัน รับ 50 เหรียญ

### สำหรับแอดมิน
- 💡 ตั้งค่า alert ให้แจ้งเตือนเมื่อมี crisis incident
- 💡 ดู trend report ทุกเช้าเพื่อเตรียม content
- 💡 ตรวจสอบ QA report ทุกสัปดาห์
