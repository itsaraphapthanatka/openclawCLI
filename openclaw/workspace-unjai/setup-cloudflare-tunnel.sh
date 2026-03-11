#!/bin/bash
# Cloudflare Tunnel Setup Script for Nong Unjai AI
# This script automates Cloudflare Tunnel installation and configuration

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

TUNNEL_NAME="${TUNNEL_NAME:-nong-unjai}"
LOCAL_PORT="${LOCAL_PORT:-8000}"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     ☁️  Cloudflare Tunnel Setup for Nong Unjai AI            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Step 1: Install cloudflared
print_status "Step 1: Installing cloudflared..."

if command -v cloudflared &> /dev/null; then
    print_success "cloudflared already installed"
else
    print_status "Downloading cloudflared..."
    
    # Detect OS and architecture
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    case $ARCH in
        x86_64)
            ARCH="amd64"
            ;;
        aarch64|arm64)
            ARCH="arm64"
            ;;
        armv7l)
            ARCH="arm"
            ;;
        *)
            print_error "Unsupported architecture: $ARCH"
            exit 1
            ;;
    esac
    
    # Download latest cloudflared
    CLOUDFLARED_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-${OS}-${ARCH}"
    
    curl -L --output /usr/local/bin/cloudflared "$CLOUDFLARED_URL"
    chmod +x /usr/local/bin/cloudflared
    
    print_success "cloudflared installed successfully"
fi

# Step 2: Authenticate with Cloudflare
print_status ""
print_status "Step 2: Authenticating with Cloudflare..."
print_status "A browser window will open. Please login to your Cloudflare account."
echo ""
read -p "Press Enter to continue..."

cloudflared tunnel login

if [ $? -ne 0 ]; then
    print_error "Authentication failed. Please try again."
    exit 1
fi

print_success "Authenticated with Cloudflare"

# Step 3: Create tunnel
print_status ""
print_status "Step 3: Creating tunnel '$TUNNEL_NAME'..."

TUNNEL_OUTPUT=$(cloudflared tunnel create "$TUNNEL_NAME" 2>&1)

if [ $? -ne 0 ]; then
    # Check if tunnel already exists
    if echo "$TUNNEL_OUTPUT" | grep -q "already exists"; then
        print_warn "Tunnel '$TUNNEL_NAME' already exists"
        
        # Get existing tunnel ID
        TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
        print_status "Using existing tunnel ID: $TUNNEL_ID"
    else
        print_error "Failed to create tunnel: $TUNNEL_OUTPUT"
        exit 1
    fi
else
    # Extract tunnel ID from output
    TUNNEL_ID=$(echo "$TUNNEL_OUTPUT" | grep -oP '(?<=Created tunnel )[a-f0-9-]+')
    print_success "Tunnel created with ID: $TUNNEL_ID"
fi

# Step 4: Create config directory and file
print_status ""
print_status "Step 4: Creating configuration..."

CONFIG_DIR="/root/.cloudflared"
mkdir -p "$CONFIG_DIR"

# Get credentials file path
CREDENTIALS_FILE="$CONFIG_DIR/${TUNNEL_ID}.json"

# Create config.yml
cat > "$CONFIG_DIR/config.yml" <<EOF
tunnel: ${TUNNEL_ID}
credentials-file: ${CREDENTIALS_FILE}

ingress:
  - hostname: ${TUNNEL_NAME}.trycloudflare.com
    service: http://localhost:${LOCAL_PORT}
  - service: http_status:404
EOF

print_success "Configuration created at $CONFIG_DIR/config.yml"

# Step 5: Create DNS route
print_status ""
print_status "Step 5: Creating DNS route..."

cloudflared tunnel route dns "$TUNNEL_NAME" "${TUNNEL_NAME}.trycloudflare.com"

if [ $? -eq 0 ]; then
    print_success "DNS route created: ${TUNNEL_NAME}.trycloudflare.com"
else
    print_warn "DNS route may already exist or failed to create"
fi

# Step 6: Create systemd service
print_status ""
print_status "Step 6: Creating systemd service..."

cat > /etc/systemd/system/cloudflared-nong-unjai.service <<EOF
[Unit]
Description=Cloudflare Tunnel for Nong Unjai AI
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/cloudflared tunnel --config /root/.cloudflared/config.yml run
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cloudflared-nong-unjai

print_success "Systemd service created and enabled"

# Step 7: Display summary
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ✅ Setup Complete!                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${CYAN}Tunnel Information:${NC}"
echo "  Name:     $TUNNEL_NAME"
echo "  ID:       $TUNNEL_ID"
echo "  URL:      https://${TUNNEL_NAME}.trycloudflare.com"
echo "  Local:    http://localhost:$LOCAL_PORT"
echo ""
echo -e "${CYAN}LINE Webhook URL:${NC}"
echo -e "  ${GREEN}https://${TUNNEL_NAME}.trycloudflare.com/webhook${NC}"
echo ""
echo -e "${CYAN}Dashboard URL:${NC}"
echo -e "  ${GREEN}https://${TUNNEL_NAME}.trycloudflare.com/dashboard${NC}"
echo ""
echo -e "${CYAN}Commands:${NC}"
echo "  Start:    sudo systemctl start cloudflared-nong-unjai"
echo "  Stop:     sudo systemctl stop cloudflared-nong-unjai"
echo "  Status:   sudo systemctl status cloudflared-nong-unjai"
echo "  Logs:     sudo journalctl -u cloudflared-nong-unjai -f"
echo ""

# Step 8: Start the tunnel
print_status "Step 8: Starting tunnel..."

# Check if local service is running
if curl -s "http://localhost:$LOCAL_PORT/health" > /dev/null 2>&1; then
    print_success "Local service is running on port $LOCAL_PORT"
else
    print_warn "Local service not detected on port $LOCAL_PORT"
    print_warn "Please start your service before running the tunnel"
fi

systemctl start cloudflared-nong-unjai

sleep 3

if systemctl is-active --quiet cloudflared-nong-unjai; then
    print_success "Tunnel is running!"
    echo ""
    echo -e "${GREEN}🎉 Your Nong Unjai AI is now accessible at:${NC}"
    echo -e "${GREEN}   https://${TUNNEL_NAME}.trycloudflare.com${NC}"
    echo ""
else
    print_error "Failed to start tunnel. Check logs with:"
    echo "  sudo journalctl -u cloudflared-nong-unjai -f"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  💡 Next Steps:                                              ║"
echo "║  1. Copy the webhook URL above                               ║"
echo "║  2. Go to LINE Developers Console                            ║"
echo "║  3. Set Webhook URL to:                                      ║"
echo "║     https://${TUNNEL_NAME}.trycloudflare.com/webhook           ║"
echo "║  4. Enable webhook and test!                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
