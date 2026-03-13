#!/bin/bash
# Get Let's Encrypt certificate (STAGING - for testing)
# Usage: ./get-cert-staging.sh your-domain.com

DOMAIN=${1:-example.com}
EMAIL=${2:-admin@example.com}

# Create directories
mkdir -p certs/live/${DOMAIN}
mkdir -p certbot-data

echo "🔒 Getting STAGING certificate for ${DOMAIN}..."
echo "   Email: ${EMAIL}"

# Run certbot
docker run -it --rm \
    -v "$(pwd)/certbot-data:/etc/letsencrypt" \
    -v "$(pwd)/certs:/etc/letsencrypt/archive" \
    -p 80:80 \
    certbot/certbot certonly \
    --standalone \
    --staging \
    --agree-tos \
    --no-eff-email \
    -m "${EMAIL}" \
    -d "${DOMAIN}" \
    -d "*.${DOMAIN}" 2>/dev/null || true

# Create symlinks
CERT_DIR="certbot-data/live/${DOMAIN}"
if [ -d "${CERT_DIR}" ]; then
    echo "✅ Certificate obtained!"
    
    # Copy to nginx ssl folder
    mkdir -p ../nginx/ssl/live/${DOMAIN}
    cp ${CERT_DIR}/fullchain.pem ../nginx/ssl/live/${DOMAIN}/
    cp ${CERT_DIR}/privkey.pem ../nginx/ssl/live/${DOMAIN}/
    
    echo "📁 Certificate files copied to nginx/ssl/"
    echo "   - fullchain.pem"
    echo "   - privkey.pem"
    echo ""
    echo "⚠️  This is a STAGING certificate (for testing only)"
    echo "   Run ./get-cert-prod.sh for production"
else
    echo "❌ Failed to get certificate"
    exit 1
fi
