#!/bin/bash
# Auto-renew Let's Encrypt certificate
# Run this via cron daily

DOMAIN=${1:-example.com}
CERT_DIR="/path/to/docker/ssl/certbot-data"
NGINX_SSL_DIR="/path/to/docker/nginx/ssl"

echo "🔄 Renewing certificate for ${DOMAIN}..."
echo "   $(date)"

# Renew certificate
docker run --rm \
    -v "${CERT_DIR}:/etc/letsencrypt" \
    -p 80:80 \
    certbot/certbot renew \
    --quiet \
    --no-self-upgrade

# Check if renewed
if [ $? -eq 0 ]; then
    echo "✅ Certificate renewed successfully"
    
    # Copy new certificate
    mkdir -p ${NGINX_SSL_DIR}/live/${DOMAIN}
    cp ${CERT_DIR}/live/${DOMAIN}/fullchain.pem ${NGINX_SSL_DIR}/live/${DOMAIN}/
    cp ${CERT_DIR}/live/${DOMAIN}/privkey.pem ${NGINX_SSL_DIR}/live/${DOMAIN}/
    
    # Reload nginx
    docker exec unjai-nginx nginx -s reload
    
    echo "   Nginx reloaded with new certificate"
else
    echo "ℹ️  No renewal needed or renewal failed"
fi

echo "   Done: $(date)"
