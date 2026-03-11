#!/bin/bash

echo "🐣 Construction AI MVP - Startup Script"
echo "========================================"

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check ports
echo ""
echo "🔍 Checking ports..."

if check_port 3000; then
    echo "⚠️  Port 3000 (Frontend) is already in use"
else
    echo "✅ Port 3000 available"
fi

if check_port 3001; then
    echo "⚠️  Port 3001 (Backend) is already in use"
else
    echo "✅ Port 3001 available"
fi

if check_port 8001; then
    echo "⚠️  Port 8001 (AI Service) is already in use"
else
    echo "✅ Port 8001 available"
fi

echo ""
echo "📦 Installing dependencies..."

# Backend
echo ""
echo "🔧 Setting up Backend..."
cd backend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

# Frontend
echo ""
echo "🎨 Setting up Frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

# AI Service
echo ""
echo "🤖 Setting up AI Service..."
cd ai-service
if ! pip show fastapi >/dev/null 2>&1; then
    pip install -r requirements.txt
fi
cd ..

echo ""
echo "🚀 Starting services..."
echo ""

# Start Backend
echo "▶️  Starting Backend (http://localhost:3001)"
cd backend
npm run dev &
BACKEND_PID=$!
cd ..

# Start AI Service
echo "▶️  Starting AI Service (http://localhost:8001)"
cd ai-service
uvicorn main:app --reload --port 8001 &
AI_PID=$!
cd ..

# Wait a bit for backend and AI to start
sleep 3

# Start Frontend
echo "▶️  Starting Frontend (http://localhost:3000)"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "✅ All services started!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:3001"
echo "🧠 AI Service: http://localhost:8001"
echo ""
echo "📚 Documentation: ./docs/MVP_GUIDE.md"
echo ""
echo "Press Ctrl+C to stop all services"
echo "========================================"

# Trap to kill all processes on exit
trap "kill $BACKEND_PID $AI_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Wait
wait
