#!/bin/bash
# Setup environment and start Construction AI MVP

echo "🐣 Setting up environment..."

# Load Node.js from nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Add pip to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify
echo "✅ Node: $(node --version)"
echo "✅ NPM: $(npm --version)"
echo "✅ Pip: $(pip --version)"

cd /home/node/.openclaw/workspace/construction-ai-mvp/

echo ""
echo "🚀 Starting services..."

# Backend
echo "▶️  Starting Backend..."
cd backend
npm install 2>&1 | tail -3
npm exec tsx src/server.ts &
BACKEND_PID=$!
cd ..

# AI Service
echo "▶️  Starting AI Service..."
cd ai-service
pip install -r requirements.txt --user --break-system-packages 2>&1 | tail -3
$HOME/.local/bin/uvicorn main:app --reload --port 8000 &
AI_PID=$!
cd ..

# Frontend
echo "▶️  Starting Frontend..."
cd frontend
npm install 2>&1 | tail -3
PORT=3000 npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "✅ All services started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend: http://localhost:3001"
echo "🧠 AI: http://localhost:8000"
echo "========================================"
echo "Press Ctrl+C to stop"

trap "kill $BACKEND_PID $AI_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
