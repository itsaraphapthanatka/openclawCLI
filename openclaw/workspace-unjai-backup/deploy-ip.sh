#!/bin/bash
# Deploy Nong Unjai AI with IP Address (No Domain)

set -e

IP_ADDRESS="${1:-136.110.50.115}"
DEPLOY_MODE="${2:-http}"  # http, cloudflare, or ngrok

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Nong Unjai AI - IP-Based Deployment                      ║"
echo "║     IP: $IP_ADDRESS                                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

case $DEPLOY_MODE in
    http)
        echo "📦 Deploying in HTTP mode (no SSL)..."
        echo ""
        echo "⚠️  WARNING: LINE Webhook requires HTTPS!"
        echo "   Use this for testing only."
        echo ""
        
        # Update docker-compose to expose port directly
        cat > docker/docker-compose.ip.yml <<EOF
version: '3.8'
services:
  line-gateway:
    ports:
      - "8000:8000"
  analytics:
    ports:
      - "8002:8002"
EOF
        
        cd docker
        docker-compose -f docker-compose.yml -f docker-compose.ip.yml up -d
        
        echo ""
        echo "✅ Deployment complete!"
        echo ""
        echo "🌐 Access URLs:"
        echo "   Gateway:   http://$IP_ADDRESS:8000"
        echo "   Health:    http://$IP_ADDRESS:8000/health"
        echo "   Analytics: http://$IP_ADDRESS:8002/dashboard"
        echo ""
        echo "⚠️  To use with LINE Webhook, you need HTTPS:"
        echo "   Option 1: ./deploy-ip.sh $IP_ADDRESS cloudflare"
        echo "   Option 2: ./deploy-ip.sh $IP_ADDRESS ngrok"
        ;;
    
    cloudflare)
        echo "☁️  Setting up Cloudflare Tunnel..."
        echo ""
        echo "Steps:"
        echo "1. Install cloudflared:"
        echo "   curl -L https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-archive-keyring.gpg"
        echo "   echo \"deb [signed-by=/usr/share/keyrings/cloudflare-archive-keyring.gpg] https://pkg.cloudflare.com/cloudflared \\\$(lsb_release -cs) main\" | sudo tee /etc/apt/sources.list.d/cloudflare.list"
        echo "   sudo apt-get update && sudo apt-get install cloudflared"
        echo ""
        echo "2. Login to Cloudflare:"
        echo "   cloudflared tunnel login"
        echo ""
        echo "3. Create tunnel:"
        echo "   cloudflared tunnel create nong-unjai"
        echo ""
        echo "4. Copy the Tunnel ID and create config file"
        echo ""
        echo "5. Run tunnel:"
        echo "   cloudflared tunnel run nong-unjai"
        echo ""
        echo "📖 Full guide: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/"
        ;;
    
    ngrok)
        echo "🌐 Setting up Ngrok..."
        echo ""
        
        # Check if ngrok is installed
        if ! command -v ngrok &> /dev/null; then
            echo "Installing ngrok..."
            curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc > /dev/null
            echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
            sudo apt update && sudo apt install ngrok
        fi
        
        # Start services first
        echo "Starting services..."
        cd docker
        docker-compose up -d
        
        echo ""
        echo "Starting ngrok..."
        echo "Press Ctrl+C to stop"
        echo ""
        
        # Run ngrok
        ngrok http 8000
        ;;
    
    *)
        echo "Usage: $0 [IP_ADDRESS] [MODE]"
        echo ""
        echo "Modes:"
        echo "  http       - HTTP only (port 8000)"
        echo "  cloudflare - Setup Cloudflare Tunnel guide"
        echo "  ngrok      - Use ngrok for temporary HTTPS"
        echo ""
        echo "Examples:"
        echo "  $0 136.110.50.115 http"
        echo "  $0 136.110.50.115 cloudflare"
        echo "  $0 136.110.50.115 ngrok"
        exit 1
        ;;
esac
