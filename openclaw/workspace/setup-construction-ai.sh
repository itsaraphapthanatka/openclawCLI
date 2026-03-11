#!/bin/bash
# Construction AI MVP - Setup Script for febc-engine
# รันที่: ~/openclawCLI/openclaw/

set -e

echo "🐣 Construction AI MVP - Auto Setup"
echo "===================================="
echo ""

PROJECT_DIR="$PWD/construction-ai-mvp"

# Create project directory
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo "📁 Creating project structure..."
mkdir -p backend/src ai-service frontend/src/app frontend/src/components docs

# ============================================
# BACKEND
# ============================================
echo "🔧 Setting up Backend..."

cat > backend/package.json << 'EOF'
{
  "name": "construction-ai-backend",
  "version": "1.0.0",
  "scripts": {
    "dev": "npx tsx src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/cors": "^2.8.17",
    "@types/node": "^20.10.0",
    "tsx": "^4.7.0",
    "typescript": "^5.3.0"
  }
}
EOF

cat > backend/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
EOF

# Backend server.ts (simplified version)
cat > backend/src/server.ts << 'EOF'
import express from 'express';
import cors from 'cors';

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

// Mock Data
const projects = [
  { id: 'PROJ-001', name: 'คอนโด High-Rise สุขุมวิท', budget: 500000000, status: 'active', riskLevel: 'green', predictedProfit: 12.5, alerts: [] },
  { id: 'PROJ-002', name: 'โรงงาน EEC ระยอง', budget: 800000000, status: 'active', riskLevel: 'yellow', predictedProfit: 8.2, alerts: [{ type: 'warning', message: 'ต้นทุนวัสดุเพิ่มขึ้น 5%' }] },
  { id: 'PROJ-003', name: 'โรงพยาบาลเชียงใหม่', budget: 1200000000, status: 'planning', riskLevel: 'red', predictedProfit: 3.5, alerts: [{ type: 'danger', message: 'กำลังคนไม่เพียงพอ' }] }
];

// Routes
app.get('/api/health', (req, res) => res.json({ status: 'ok' }));

app.get('/api/dashboard/summary', (req, res) => {
  res.json({
    totalProjects: projects.length,
    activeProjects: projects.filter(p => p.status === 'active').length,
    totalBudget: projects.reduce((s, p) => s + p.budget, 0),
    avgProfit: (projects.reduce((s, p) => s + p.predictedProfit, 0) / projects.length).toFixed(1),
    trafficLight: {
      green: projects.filter(p => p.riskLevel === 'green').length,
      yellow: projects.filter(p => p.riskLevel === 'yellow').length,
      red: projects.filter(p => p.riskLevel === 'red').length,
    }
  });
});

app.get('/api/projects', (req, res) => res.json(projects));

app.get('/api/esg/summary', (req, res) => {
  res.json({
    carbon: { totalReduction: 23, target: 50 },
    safety: { avgScore: 95, daysWithoutAccident: 365 },
    happiness: { avgScore: 4.5, totalEmployees: 150 }
  });
});

app.listen(PORT, () => console.log(`🚀 Backend: http://localhost:${PORT}`));
EOF

# ============================================
# AI SERVICE
# ============================================
echo "🤖 Setting up AI Service..."

cat > ai-service/requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn==0.27.0
numpy==1.26.3
scikit-learn==1.4.0
EOF

cat > ai-service/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI(title="Construction AI Service")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
async def health(): 
    return {"status": "ok"}

@app.post("/predict")
async def predict(request: dict):
    return {
        "prediction": {
            "shouldAccept": random.random() > 0.3,
            "predictedProfit": round(random.uniform(5, 15), 2),
            "riskScore": random.randint(20, 80),
            "confidence": round(random.uniform(0.75, 0.95), 2),
            "recommendation": "ACCEPT" if random.random() > 0.3 else "NEGOTIATE"
        }
    }

@app.post("/forecast")
async def forecast(request: dict):
    forecast = [{"month": i+1, "predicted": round(5 + i * 1.2, 2)} for i in range(12)]
    return {"forecast": forecast, "summary": {"avgProfit": 10.5, "trend": "UP", "confidence": 0.88}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# ============================================
# FRONTEND
# ============================================
echo "🎨 Setting up Frontend..."

cat > frontend/package.json << 'EOF'
{
  "name": "construction-ai-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "recharts": "^2.10.0",
    "lucide-react": "^0.309.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
EOF

cat > frontend/next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [{ source: '/api/:path*', destination: 'http://localhost:3001/api/:path*' }];
  },
};
module.exports = nextConfig;
EOF

cat > frontend/tailwind.config.js << 'EOF'
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: { extend: {} },
  plugins: [],
};
EOF

cat > frontend/postcss.config.js << 'EOF'
module.exports = {
  plugins: { tailwindcss: {}, autoprefixer: {} },
};
EOF

mkdir -p frontend/src/app frontend/src/components

cat > frontend/src/app/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF

cat > frontend/src/app/layout.tsx << 'EOF'
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <body className="antialiased bg-gray-50">{children}</body>
    </html>
  );
}
EOF

cat > frontend/src/app/page.tsx << 'EOF'
'use client';
import { useEffect, useState } from 'react';
import axios from 'axios';
import { Building2, AlertTriangle, Shield, Activity, Leaf, Users } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const mockForecast = [
  { month: 'M1', predicted: 5.2 }, { month: 'M2', predicted: 6.5 },
  { month: 'M3', predicted: 7.8 }, { month: 'M4', predicted: 9.1 },
  { month: 'M5', predicted: 10.5 }, { month: 'M6', predicted: 11.8 },
];

export default function Home() {
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    axios.get('/api/dashboard/summary').then(r => setSummary(r.data));
  }, []);

  if (!summary) return <div className="flex justify-center p-10">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">🏗️ Construction AI Dashboard</h1>
        <p className="text-gray-600">{new Date().toLocaleDateString('th-TH')}</p>
      </header>

      {/* Traffic Lights */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-6 rounded shadow border-l-4 border-green-500">
          <div className="flex justify-between">
            <div><p className="text-sm text-gray-600">ปกติ</p><p className="text-3xl font-bold text-green-600">{summary.trafficLight.green}</p></div>
            <Shield className="h-10 w-10 text-green-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded shadow border-l-4 border-yellow-500">
          <div className="flex justify-between">
            <div><p className="text-sm text-gray-600">ติดตาม</p><p className="text-3xl font-bold text-yellow-600">{summary.trafficLight.yellow}</p></div>
            <AlertTriangle className="h-10 w-10 text-yellow-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded shadow border-l-4 border-red-500">
          <div className="flex justify-between">
            <div><p className="text-sm text-gray-600">เร่งด่วน</p><p className="text-3xl font-bold text-red-600">{summary.trafficLight.red}</p></div>
            <Activity className="h-10 w-10 text-red-500" />
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded shadow"><p className="text-sm text-gray-600">โครงการ</p><p className="text-2xl font-bold">{summary.totalProjects}</p></div>
        <div className="bg-white p-4 rounded shadow"><p className="text-sm text-gray-600">กำลังดำเนินการ</p><p className="text-2xl font-bold">{summary.activeProjects}</p></div>
        <div className="bg-white p-4 rounded shadow"><p className="text-sm text-gray-600">งบประมาณ</p><p className="text-2xl font-bold">{(summary.totalBudget/1e9).toFixed(1)}B</p></div>
        <div className="bg-white p-4 rounded shadow"><p className="text-sm text-gray-600">กำไรเฉลี่ย</p><p className="text-2xl font-bold text-green-600">{summary.avgProfit}%</p></div>
      </div>

      {/* Chart */}
      <div className="bg-white p-6 rounded shadow mb-6">
        <h3 className="text-lg font-semibold mb-4">📈 AI Profit Forecast</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockForecast}>
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="predicted" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ESG */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded shadow text-center">
          <Leaf className="h-10 w-10 text-green-500 mx-auto mb-2" />
          <p className="text-2xl font-bold text-green-600">23</p>
          <p className="text-sm text-gray-600">ตันคาร์บอนลดได้</p>
        </div>
        <div className="bg-white p-4 rounded shadow text-center">
          <Shield className="h-10 w-10 text-blue-500 mx-auto mb-2" />
          <p className="text-2xl font-bold text-blue-600">365</p>
          <p className="text-sm text-gray-600">วันไร้อุบัติเหตุ</p>
        </div>
        <div className="bg-white p-4 rounded shadow text-center">
          <Users className="h-10 w-10 text-purple-500 mx-auto mb-2" />
          <p className="text-2xl font-bold text-purple-600">4.5/5</p>
          <p className="text-sm text-gray-600">ความพึงพอใจ</p>
        </div>
      </div>
    </div>
  );
}
EOF

# ============================================
# START SCRIPT
# ============================================
cat > start.sh << 'EOF'
#!/bin/bash
echo "🐣 Starting Construction AI MVP..."
cd backend && npm install && npm run dev &
cd ../ai-service && pip install -r requirements.txt && uvicorn main:app --reload --port 8000 &
cd ../frontend && npm install && npm run dev &
echo "✅ All services starting..."
echo "📱 Open http://localhost:3000"
wait
EOF
chmod +x start.sh

# ============================================
# README
# ============================================
cat > README.md << 'EOF'
# Construction AI MVP

ระบบ AI-Powered Construction Intelligence Platform

## 🚀 Quick Start

```bash
./start.sh
```

เปิด: http://localhost:3000

## 📁 Structure
- `backend/` - Express API (Port 3001)
- `ai-service/` - Python FastAPI (Port 8000)
- `frontend/` - Next.js Dashboard (Port 3000)
EOF

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📂 Project location: $PROJECT_DIR"
echo ""
echo "To start the application:"
echo "  cd $PROJECT_DIR"
echo "  ./start.sh"
echo ""
echo "Then open: http://localhost:3000"
