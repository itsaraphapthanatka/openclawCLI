#!/bin/bash
# Start Construction AI MVP on febc-engine

echo "🐣 Starting Construction AI MVP..."

# Load Node.js from nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Add pip to PATH
export PATH="$HOME/.local/bin:$PATH"

# Go to project directory
PROJECT_DIR="$HOME/openclawCLI/openclaw/workspace/construction-ai-mvp"
cd "$PROJECT_DIR"

echo "✅ Node: $(node --version)"
echo "✅ NPM: $(npm --version)"
echo "✅ Pip: $(pip --version)"

# Kill old processes
killall -9 node 2>/dev/null
sleep 2

echo ""
echo "🚀 Starting services..."

# Backend
echo "▶️  Starting Backend..."
cd "$PROJECT_DIR/backend"
npm install 2>&1 | tail -3
npm exec tsx src/server.ts &
BACKEND_PID=$!

echo "✅ Backend PID: $BACKEND_PID"

# AI Service  
echo "▶️  Starting AI Service..."
cd "$PROJECT_DIR/ai-service"
pip install -r requirements.txt --user --break-system-packages 2>&1 | tail -3
$HOME/.local/bin/uvicorn main:app --reload --port 8000 &
AI_PID=$!

echo "✅ AI Service PID: $AI_PID"

# Wait for services to start
sleep 10

echo ""
echo "========================================"
echo "✅ Services started!"
echo "🔌 Backend: http://localhost:3001"
echo "🧠 AI: http://localhost:8000"
echo ""
echo "⚠️  Frontend มีปัญหา Permission"
echo "📱 ใช้แทน: http://localhost:3001 (Backend serve HTML)"
echo "========================================"
echo ""
echo "กด Ctrl+C เพื่อหยุด"

trap "kill $BACKEND_PID $AI_PID 2>/dev/null; exit" INT
wait
