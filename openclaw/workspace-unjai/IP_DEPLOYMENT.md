# IP-Based Deployment Guide

## 🎯 ใช้ IP แทน Domain

เมื่อไม่มี Domain Name สามารถใช้ IP Address ได้โดยต้องปรับ:

### ข้อจำกัด
- ❌ ไม่สามารถใช้ Let's Encrypt SSL ได้ (ต้องใช้ Domain)
- ⚠️ LINE Webhook ต้องเป็น HTTPS (ต้องใช้ Self-signed certificate หรือ Cloudflare Tunnel)

### ทางเลือกที่ใช้ได้
1. **HTTP Only** (สำหรับทดสอบภายใน)
2. **Self-signed SSL** (ทดสอบระบบ HTTPS)
3. **Cloudflare Tunnel** (แนะนำ - ได้ HTTPS ฟรี)
4. **Ngrok** (สำหรับทดสอบชั่วคราว)

---

## 🚀 Option 1: HTTP Only (เร็วที่สุด)

### Docker Compose

```bash
# ใช้ docker-compose ธรรมดา (ไม่ต้องใช้ ssl)
cd docker
docker-compose up -d

# ระบบจะรันที่
http://136.110.50.115:8000
```

### ตั้งค่า LINE Webhook

```
# ต้องใช้ Ngrok หรือ Cloudflare Tunnel
# เพราะ LINE กำหนดให้ต้องเป็น HTTPS เท่านั้น
```

---

## 🔒 Option 2: Self-signed SSL

### สร้าง Certificate

```bash
cd docker/ssl

# สร้าง self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout selfsigned.key \
  -out selfsigned.crt \
  -subj "/CN=136.110.50.115"

# Copy ไป nginx
cp selfsigned.crt ../nginx/ssl/
cp selfsigned.key ../nginx/ssl/
```

### ตั้งค่า Nginx

```nginx
server {
    listen 443 ssl;
    server_name 136.110.50.115;
    
    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
    
    # ... rest of config
}
```

⚠️ **ข้อควรระวัง**: LINE อาจไม่ยอมรับ self-signed certificate

---

## ☁️ Option 3: Cloudflare Tunnel (แนะนำ)

### วิธีติดตั้ง

```bash
# 1. สมัคร Cloudflare
# ไปที่ https://dash.cloudflare.com

# 2. ติดตั้ง cloudflared
curl -L https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/cloudflare-archive-keyring.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflare.list
sudo apt-get update && sudo apt-get install cloudflared

# 3. Login
cloudflared tunnel login

# 4. สร้าง tunnel
cloudflared tunnel create nong-unjai

# 5. รับ Tunnel ID และใส่ใน config
cloudflared tunnel route dns nong-unjai nong-unjai.yourdomain.com

# 6. สร้าง config file
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml <<EOF
tunnel: YOUR_TUNNEL_ID
credentials-file: /root/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: nong-unjai.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
EOF

# 7. รัน tunnel
cloudflared tunnel run nong-unjai
```

### ข้อดี
- ✅ ได้ HTTPS ฟรี
- ✅ ได้ Domain ฟรี (nong-unjai.yourdomain.com)
- ✅ LINE Webhook ทำงานได้
- ✅ ไม่ต้องเปิด port บน server

---

## 🌐 Option 4: Ngrok (ทดสอบชั่วคราว)

```bash
# ติดตั้ง ngrok
# https://ngrok.com/download

# รัน ngrok
ngrok http 8000

# จะได้ URL แบบนี้
# https://abc123.ngrok-free.app

# เอาไปใส่ใน LINE Webhook
```

---

## 📋 สรุป

| วิธี | SSL | LINE Webhook | ความยาก | แนะนำ |
|------|-----|--------------|---------|-------|
| HTTP Only | ❌ | ❌ | ⭐ | ทดสอบภายใน |
| Self-signed | ⚠️ | ❌ | ⭐⭐ | ไม่แนะนำ |
| Cloudflare Tunnel | ✅ | ✅ | ⭐⭐⭐ | **แนะนำ** |
| Ngrok | ✅ | ✅ | ⭐ | ทดสอบชั่วคราว |

---

## 🔧 ตั้งค่า Environment สำหรับ IP

```bash
# .env file
DOMAIN=136.110.50.115
USE_SSL=false

# LINE (ต้องใช้ HTTPS จริงๆ ถึงจะทำงานได้)
LINE_CHANNEL_SECRET=xxx
LINE_CHANNEL_ACCESS_TOKEN=xxx

# Database
POSTGRES_HOST=postgres
POSTGRES_PASSWORD=xxx

# Redis
REDIS_HOST=redis
REDIS_PASSWORD=xxx
```

---

## 🚀 Quick Start with IP

```bash
# 1. Clone
git clone <repo>
cd nong-unjai-ai

# 2. แก้ไข .env
sed -i 's/DOMAIN=.*/DOMAIN=136.110.50.115/' docker/.env

# 3. Deploy แบบ HTTP
cd docker
docker-compose up -d

# 4. Test
http://136.110.50.115:8000/health

# 5. ตั้งค่า Cloudflare Tunnel (แนะนำ)
# ตามขั้นตอน Option 3 ด้านบน
```
