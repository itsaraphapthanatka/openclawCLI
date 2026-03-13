#!/bin/bash
# สคริปต์ตัดคลิปวิดีโอสำหรับ Nong Unjai
# ใช้ร่วมกับ Pinecone Clip URL

# ตัวอย่าง: ตัดคลิป "หกล้มคือปัญหาปกติ"
VIDEO_ID="capZNT7BYe8"
START_TIME=3
END_TIME=5
OUTPUT_NAME="${VIDEO_ID}_${START_TIME}_${END_TIME}.mp4"

# 1. ดาวน์โหลดจาก YouTube
echo "กำลังดาวน์โหลดวิดีโอ..."
yt-dlp -f "best[ext=mp4]" -o "%(id)s.%(ext)s" "https://www.youtube.com/watch?v=${VIDEO_ID}"

# 2. ตัดคลิปตามช่วงเวลา
echo "กำลังตัดคลิป ${START_TIME}-${END_TIME} วินาที..."
ffmpeg -ss 00:00:${START_TIME} -t $((${END_TIME}-${START_TIME})) -i "${VIDEO_ID}.mp4" -c copy -y "${OUTPUT_NAME}"

# 3. ตรวจสอบไฟล์
echo "ไฟล์ที่สร้าง: ${OUTPUT_NAME}"
ls -lh "${OUTPUT_NAME}"

echo ""
echo "✅ ตัดคลิปเสร็จแล้ว!"
echo "📁 ไฟล์: ${OUTPUT_NAME}"
echo ""
echo "ต่อไปอัปโหลดด้วยคำสั่ง:"
echo "scp ${OUTPUT_NAME} root@nongaunjai.febradio.org:/var/www/html/static/clips/"
