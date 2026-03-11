"""
LINE Gateway Service Entry Point
"""
import os
import sys

# เพิ่ม path เพื่อให้หาโมดูลในโฟลเดอร์ modules เจอ
sys.path.insert(0, '/app/modules')

# Import มาทั้งตัว create_app และตัวคลาสหลัก (สมมติว่าชื่อ LineGateway)
from module_4_line_gateway import create_app, LineGateway

if __name__ == "__main__":
    import uvicorn
    
    # 1. สร้าง Instance ของ Gateway ขึ้นมาก่อน
    gateway_instance = LineGateway()
    
    # 2. ส่ง instance เข้าไปใน create_app ตามที่ Error แจ้งว่ามันต้องการ
    app = create_app(gateway=gateway_instance)
    
    # ดึงค่า Config จาก Environment Variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"🚀 Starting LINE Gateway on {host}:{port}")
    uvicorn.run(app, host=host, port=port)