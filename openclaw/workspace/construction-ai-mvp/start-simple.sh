#!/bin/bash
# Simple start script - Backend only with HTML frontend

echo "🐣 Starting Construction AI MVP..."

# Kill old processes
killall -9 node 2>/dev/null

# Start Backend
cd /home/node/.openclaw/workspace/construction-ai-mvp/backend
npm exec tsx src/server.ts &

echo ""
echo "✅ Backend running at: http://localhost:3001"
echo "🌐 Dashboard: http://localhost:3001"
echo ""
echo "กด Ctrl+C เพื่อหยุด"
wait
