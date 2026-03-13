#!/bin/bash
# อัปโหลดคลิปขึ้นเซิร์ฟเวอร์ Nong Unjai

# ตัวแปร
SERVER="nongaunjai.febradio.org"
USER="root"
REMOTE_PATH="/var/www/html/static/clips/"
CLIP_FILE=$1

if [ -z "$CLIP_FILE" ]; then
    echo "❌ ใช้งาน: ./upload_clip.sh <ชื่อไฟล์.mp4>"
    echo "ตัวอย่าง: ./upload_clip.sh capZNT7BYe8_3_5.mp4"
    exit 1
fi

# ตรวจสอบไฟล์มีอยู่ไหม
if [ ! -f "$CLIP_FILE" ]; then
    echo "❌ ไม่พบไฟล์: $CLIP_FILE"
    exit 1
fi

echo "📤 กำลังอัปโหลด $CLIP_FILE ขึ้นเซิร์ฟเวอร์..."

# อัปโหลดด้วย scp
scp "$CLIP_FILE" "${USER}@${SERVER}:${REMOTE_PATH}"

if [ $? -eq 0 ]; then
    echo "✅ อัปโหลดสำเร็จ!"
    echo ""
    echo "🌐 URL ที่ใช้งานได้:"
    echo "https://${SERVER}/static/clips/${CLIP_FILE}"
    echo ""
    echo "ทดสอบเปิดดูได้เลย!"
else
    echo "❌ อัปโหลดล้มเหลว"
    echo "ตรวจสอบ:"
    echo "  - มีสิทธิ์ SSH เข้าเซิร์ฟเวอร์หรือไม่"
    echo "  - path บนเซิร์ฟเวอร์ถูกต้องหรือไม่"
fi
