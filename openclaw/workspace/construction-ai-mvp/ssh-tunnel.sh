#!/bin/bash
# SSH Port Forwarding Script
# รันที่เครื่องของคุณ (ไม่ใช่ที่เซิร์ฟเวอร์)

echo "🔄 กำลังสร้าง SSH Tunnel..."
echo "คำสั่งที่ต้องรันที่เครื่องคุณ:"
echo ""
echo "  ssh -L 3001:localhost:3001 febc-engine"
echo ""
echo "หรือถ้าใช้ key:"
echo ""
echo "  ssh -L 3001:localhost:3001 -i ~/.ssh/your-key febc-engine"
echo ""
echo "แล้วเปิด http://localhost:3001 ที่เบราว์เซอร์"
