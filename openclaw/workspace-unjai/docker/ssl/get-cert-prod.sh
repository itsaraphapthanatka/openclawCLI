#!/bin/bash
# Get Let's Encrypt certificate (PRODUCTION)
# Usage: ./get-cert-prod.sh your-domain.com admin@example.com

DOMAIN=${1:-example.com}
EMAIL=${2:-admin@example.com}

# Create directories
mkdir -p certs/live/${DOMAIN}
mkdir -p certbot-data

echo "🔒 Getting PRODUCTION certificate for ${DOMAIN}..."
echo "   Email: ${EMAIL}"
echo ""
echo "⚠️  Rate limits apply: 50 certs per domain per week"
read -p "Continue? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 1
fi

# Run certbot
docker run -it --rm \
    -v "$(pwd)/certbot-data:/etc/letsencrypt" \
    -v "$(pwd)/certs:/etc/letsencrypt/archive" \
    -p 80:80 \
    certbot/certbot certonly \
    --standalone \
    --agree-tos \
    --no-eff-email \
    -m "${EMAIL}" \
    -d "${DOMAIN}" \
    -d "*.${DOMAIN}" 2>/dev/null || true

# Create symlinks
CERT_DIR="certbot-data/live/${DOMAIN}"
if [ -d "${CERT_DIR}" ]; then
    echo "✅ Production certificate obtained!"
    
    # Copy to nginx ssl folder
    mkdir -p ../nginx/ssl/live/${DOMAIN}
    cp ${CERT_DIR}/fullchain.pem ../nginx/ssl/live/${DOMAIN}/
    cp ${CERT_DIR}/privkey.pem ../nginx/ssl/live/${DOMAIN}/
    
    echo "📁 Certificate files copied to nginx/ssl/"
    echo "   - fullchain.pem"
    echo "   - privkey.pem"
    echo ""
    echo "🚀 Ready to deploy with SSL!"
    echo "   docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d"
else
    echo "❌ Failed to get certificate"
    exit 1
fi
