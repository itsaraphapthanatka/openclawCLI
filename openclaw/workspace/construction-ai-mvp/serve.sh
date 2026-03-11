#!/bin/bash
# Start simple HTTP server for Construction AI MVP Dashboard

cd /home/node/.openclaw/workspace/construction-ai-mvp

echo "🐣 Starting HTTP Server..."
echo "📱 Dashboard: http://localhost:8080/dashboard.html"
echo "🔌 API Backend: http://localhost:3001"
echo ""
echo "กด Ctrl+C เพื่อหยุด"
echo ""

python3 -m http.server 8080
