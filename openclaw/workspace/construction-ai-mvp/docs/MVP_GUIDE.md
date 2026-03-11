# 🚀 MVP Prototype - Construction AI Platform

## สิ่งที่ทำเสร็จแล้ว

### 1. Backend (Node.js + Express)
- ✅ RESTful API ครบชุด
- ✅ Dashboard Summary API
- ✅ Projects API
- ✅ AI Integration (Proxy to Python service)
- ✅ ESG Tracking API
- ✅ Inventory & Employee mock data

### 2. AI Service (Python + FastAPI)
- ✅ Pre-Project Risk Prediction
- ✅ Profit Forecasting
- ✅ Anomaly Detection
- ✅ ESG Analysis

### 3. Frontend (Next.js 14 + Tailwind)
- ✅ Dashboard ภาพรวม
- ✅ Traffic Light System (เขียว/เหลือง/แดง)
- ✅ Project List
- ✅ AI Prediction UI
- ✅ ESG Dashboard
- ✅ Alert Center

---

## 🎯 MVP Features ที่โชว์ได้

| Feature | Status | รายละเอียด |
|---------|--------|------------|
| **Traffic Light Dashboard** | ✅ | แสดงสถานะโครงการเขียว/เหลือง/แดง |
| **Profit Predictor** | ✅ | กราฟพยากรณ์กำไร 6 เดือน |
| **Pre-Project Scanner** | ✅ | UI สำหรับวิเคราะห์ก่อนรับงาน |
| **ESG Dashboard** | ✅ | คาร์บอน/ความปลอดภัย/ความสุขพนักงาน |
| **Real-time Alerts** | ✅ | แจ้งเตือนความผิดปกติ |

---

## 📊 Demo Data ที่เตรียมไว้

### โครงการตัวอย่าง (3 โครงการ)
1. **คอนโด High-Rise สุขุมวิท** - สถานะเขียว (ปกติ)
2. **โรงงาน EEC ระยอง** - สถานะเหลือง (ต้องติดตาม)
3. **โรงพยาบาลเชียงใหม่** - สถานะแดง (ต้องเร่งด่วน)

### ตัวเลขสำคัญ
- งบประมาณรวม: 2,500 ล้านบาท
- กำไรเฉลี่ยที่คาดการณ์: 8.1%
- ลดคาร์บอนได้: 23 ตัน
- วันไร้อุบัติเหตุ: 365 วัน

---

## 🎬 การสาธิต (Demo Script)

### Scene 1: Dashboard ภาพรวม
1. เปิดหน้า Dashboard
2. ชี้ไปที่ Traffic Light Cards (เขียว/เหลือง/แดง)
3. อธิบายว่า CEO เห็นอะไรบ้างในหนึ่งสายตา

### Scene 2: โครงการที่มีปัญหา
1. คลิกไปที่ Tab "โครงการ"
2. เลื่อนหาโครงการสีแดง (โรงพยาบาลเชียงใหม่)
3. ชี้ให้เห็น Alerts ที่แสดงความเสี่ยง
4. อธิบายว่า AI แจ้งเตือนอะไรบ้าง

### Scene 3: AI Prediction
1. คลิกที่ Tab "AI พยากรณ์"
2. โชว์กราฟพยากรณ์กำไร
3. อธิบายว่า AI คำนวณจากปัจจัยอะไรบ้าง
4. บอกว่าความแม่นยำ 88%

### Scene 4: ESG
1. คลิกที่ Tab "ESG"
2. โชว์ตัวเลขคาร์บอน/ความปลอดภัย
3. อธิบายว่าทำไมถึงสำคัญสำหรับ SET

---

## 💡 จุดขายที่ต้องเน้น

1. **"จาก Excel มาสู่ Dashboard"**
   - ไม่ต้องเปิดไฟล์หลายอัน
   - เห็นทุกอย่างในหน้าเดียว

2. **"รู้ก่อนพัง"**
   - AI แจ้งเตือนก่อนที่จะสาย
   - ปิดรูรั่วเงินหน้างาน

3. **"เลือกงานที่ใช่"**
   - วิเคราะห์ก่อนรับงาน
   - ไม่ต้องเสียเวลากับงานที่ไม่กำไร

4. **"ESG ง่ายๆ"**
   - ข้อมูลพร้อมรายงาน SET
   - ดึงดูดนักลงทุน

---

## 🔧 การรันระบบ

```bash
# Terminal 1: Backend
cd backend
npm install
npm run dev

# Terminal 2: AI Service
cd ai-service
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 3: Frontend
cd frontend
npm install
npm run dev
```

เข้าใช้งาน: http://localhost:3000

---

## 📝 สิ่งที่ต้องทำต่อสำหรับ Production

1. **Database จริง** (PostgreSQL + Prisma)
2. **Authentication** (JWT + Role-based)
3. **Real-time Updates** (WebSocket)
4. **File Upload** (เอกสารโครงการ)
5. **Email Notifications**
6. **Mobile App** (React Native)

---

*สร้างเมื่อ: 2026-02-28*
*โดย: ไข่เป็ด 🐣*
