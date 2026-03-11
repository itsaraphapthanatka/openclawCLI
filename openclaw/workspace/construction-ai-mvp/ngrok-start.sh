#!/bin/bash
# ngrok setup script for Construction AI MVP

echo "🌐 สร้าง Public URL ด้วย ngrok"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "⚠️ ngrok ยังไม่ได้ติดตั้ง"
    echo ""
    echo "ติดตั้งโดยรันคำสั่งนี้:"
    echo "  curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null"
    echo "  echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | sudo tee /etc/apt/sources.list.d/ngrok.list"
    echo "  sudo apt update && sudo apt install ngrok"
    echo ""
    echo "แล้วตั้งค่า authtoken:"
    echo "  ngrok config add-authtoken YOUR_TOKEN"
    exit 1
fi

echo "🚀 กำลังสร้าง tunnel ไปยัง port 3001..."
ngrok http 3001
