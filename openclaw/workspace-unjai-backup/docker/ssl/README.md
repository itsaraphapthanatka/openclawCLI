# SSL/HTTPS Setup with Let's Encrypt

## 🎯 Quick Start

```bash
# 1. Install certbot
cd docker/ssl

# 2. Get certificate (staging first)
./get-cert-staging.sh your-domain.com

# 3. Test works, then get production cert
./get-cert-prod.sh your-domain.com

# 4. Start with SSL
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d
```

## 📁 Files

| File | Purpose |
|------|---------|
| `get-cert-staging.sh` | Get test certificate |
| `get-cert-prod.sh` | Get production certificate |
| `renew-cert.sh` | Auto-renewal cron job |
| `docker-compose.ssl.yml` | SSL override |

## 🔒 How It Works

```
User ──HTTPS──▶ Nginx ──HTTP──▶ Services
         ↑
    Let's Encrypt
    (Auto-renew)
```

## 📋 Prerequisites

- Domain pointing to server
- Port 80 open (for ACME challenge)
- Port 443 open (for HTTPS)

## 🚀 Deployment Steps

### 1. DNS Setup

```
A Record: your-domain.com → YOUR_SERVER_IP
```

### 2. Get Certificate

```bash
cd docker/ssl
chmod +x *.sh

# Test with staging (no rate limits)
./get-cert-staging.sh nong-unjai.example.com

# Check certificate
openssl x509 -in certs/live/nong-unjai.example.com/cert.pem -text -noout

# Production (rate limited!)
./get-cert-prod.sh nong-unjai.example.com
```

### 3. Start with SSL

```bash
cd docker
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d
```

### 4. Auto-Renewal

```bash
# Add to crontab
crontab -e

# Add line:
0 3 * * * /path/to/docker/ssl/renew-cert.sh >> /var/log/cert-renewal.log 2>&1
```

## 🔧 Configuration

### Environment Variables (add to .env)

```env
# SSL
DOMAIN=nong-unjai.example.com
EMAIL=admin@example.com
NGINX_HTTPS_PORT=443
```

### nginx SSL Config

```nginx
server {
    listen 443 ssl http2;
    server_name nong-unjai.example.com;

    ssl_certificate /etc/nginx/ssl/live/nong-unjai.example.com/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/live/nong-unjai.example.com/privkey.pem;

    # SSL Best Practices
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

## 🧪 Testing

```bash
# Test SSL
curl -v https://your-domain.com/health

# Test grade
nmap --script ssl-enum-ciphers -p 443 your-domain.com

# Online test
# https://www.ssllabs.com/ssltest/
```
