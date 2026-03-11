import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios from 'axios';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

app.use(cors());
app.use(express.json());

// Mock Database
const projects = [
  {
    id: 'PROJ-001',
    name: 'คอนโด High-Rise สุขุมวิท',
    budget: 500000000,
    duration: 18,
    status: 'active',
    riskLevel: 'green',
    predictedProfit: 12.5,
    actualProfit: 11.8,
    alerts: [],
    esg: {
      carbonReduction: 15,
      safetyScore: 98,
      employeeSatisfaction: 4.5
    }
  },
  {
    id: 'PROJ-002',
    name: 'โรงงาน EEC ระยอง',
    budget: 800000000,
    duration: 24,
    status: 'active',
    riskLevel: 'yellow',
    predictedProfit: 8.2,
    actualProfit: 6.5,
    alerts: [
      { type: 'warning', message: 'ต้นทุนวัสดุเพิ่มขึ้น 5% จากแผน', timestamp: '2026-02-27' }
    ],
    esg: {
      carbonReduction: 8,
      safetyScore: 92,
      employeeSatisfaction: 4.2
    }
  },
  {
    id: 'PROJ-003',
    name: 'โรงพยาบาลเชียงใหม่',
    budget: 1200000000,
    duration: 30,
    status: 'planning',
    riskLevel: 'red',
    predictedProfit: 3.5,
    actualProfit: null,
    alerts: [
      { type: 'danger', message: 'กำลังคนไม่เพียงพอสำหรับ Timeline', timestamp: '2026-02-28' },
      { type: 'warning', message: 'Client มีประวัติจ่ายเงินล่าชา 20%', timestamp: '2026-02-25' }
    ],
    esg: {
      carbonReduction: 0,
      safetyScore: 0,
      employeeSatisfaction: 0
    }
  }
];

const materials = [
  { id: 1, name: 'เหล็กเส้น SD40', stock: 150, unit: 'ตัน', minStock: 100, price: 25000 },
  { id: 2, name: 'ปูนซีเมนต์', stock: 500, unit: 'ถุง', minStock: 300, price: 180 },
  { id: 3, name: 'คอนกรีตผสมเสร็จ', stock: 200, unit: 'ลบ.ม.', minStock: 150, price: 3200 },
];

const employees = [
  { id: 'EMP001', name: 'สมชาย ใจดี', position: 'วิศวกรโยธา', project: 'PROJ-001', happiness: 4.8, hoursThisWeek: 45 },
  { id: 'EMP002', name: 'สมหญิง รักงาน', position: 'โฟร์แมน', project: 'PROJ-002', happiness: 4.2, hoursThisWeek: 52 },
  { id: 'EMP003', name: 'มานี ขยัน', position: 'ช่างก่อสร้าง', project: 'PROJ-001', happiness: 3.9, hoursThisWeek: 58 },
];

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Dashboard Summary
app.get('/api/dashboard/summary', (req, res) => {
  const totalProjects = projects.length;
  const activeProjects = projects.filter(p => p.status === 'active').length;
  const totalBudget = projects.reduce((sum, p) => sum + p.budget, 0);
  const avgProfit = projects.reduce((sum, p) => sum + p.predictedProfit, 0) / projects.length;
  const alerts = projects.flatMap(p => p.alerts.map(a => ({ ...a, projectId: p.id, projectName: p.name })));
  
  res.json({
    totalProjects,
    activeProjects,
    totalBudget,
    avgProfit: avgProfit.toFixed(2),
    alerts,
    trafficLight: {
      green: projects.filter(p => p.riskLevel === 'green').length,
      yellow: projects.filter(p => p.riskLevel === 'yellow').length,
      red: projects.filter(p => p.riskLevel === 'red').length,
    }
  });
});

// Projects
app.get('/api/projects', (req, res) => {
  res.json(projects);
});

app.get('/api/projects/:id', (req, res) => {
  const project = projects.find(p => p.id === req.params.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });
  res.json(project);
});

// AI Prediction - Pre Project
app.post('/api/ai/predict-project', async (req, res) => {
  const { projectData } = req.body;
  
  try {
    // Call AI Service
    const response = await axios.post(`${AI_SERVICE_URL}/predict`, {
      type: 'pre_project',
      data: projectData
    });
    
    res.json(response.data);
  } catch (error) {
    // Fallback to mock
    res.json({
      prediction: {
        shouldAccept: Math.random() > 0.3,
        predictedProfit: (Math.random() * 15 + 2).toFixed(2),
        riskScore: Math.floor(Math.random() * 100),
        confidence: 0.85,
        factors: [
          { name: 'Client History', score: 85, impact: 'positive' },
          { name: 'Material Cost Trend', score: 65, impact: 'negative' },
          { name: 'Labor Availability', score: 90, impact: 'positive' },
        ],
        recommendation: Math.random() > 0.3 ? 'ACCEPT' : 'NEGOTIATE'
      }
    });
  }
});

// AI Prediction - Profit Forecast
app.post('/api/ai/forecast-profit', async (req, res) => {
  const { projectId, months } = req.body;
  
  try {
    const response = await axios.post(`${AI_SERVICE_URL}/forecast`, {
      type: 'profit',
      projectId,
      months
    });
    
    res.json(response.data);
  } catch (error) {
    // Generate mock forecast
    const forecast = [];
    let currentProfit = 5.0;
    
    for (let i = 0; i < (months || 12); i++) {
      currentProfit += (Math.random() - 0.4) * 2;
      forecast.push({
        month: i + 1,
        predicted: Math.max(0, currentProfit.toFixed(2)),
        optimistic: (currentProfit + 2).toFixed(2),
        pessimistic: Math.max(0, (currentProfit - 2).toFixed(2))
      });
    }
    
    res.json({
      forecast,
      summary: {
        avgProfit: (forecast.reduce((s, f) => s + parseFloat(f.predicted), 0) / forecast.length).toFixed(2),
        trend: forecast[forecast.length - 1].predicted > forecast[0].predicted ? 'UP' : 'DOWN',
        confidence: 0.88
      }
    });
  }
});

// Inventory
app.get('/api/inventory', (req, res) => {
  res.json(materials);
});

// Employees
app.get('/api/employees', (req, res) => {
  res.json(employees);
});

// ESG Dashboard
app.get('/api/esg/summary', (req, res) => {
  const activeProjects = projects.filter(p => p.status === 'active');
  
  res.json({
    carbon: {
      totalReduction: activeProjects.reduce((s, p) => s + p.esg.carbonReduction, 0),
      target: 50,
      unit: 'tons'
    },
    safety: {
      avgScore: (activeProjects.reduce((s, p) => s + p.esg.safetyScore, 0) / activeProjects.length).toFixed(1),
      incidents: 0,
      daysWithoutAccident: 365
    },
    happiness: {
      avgScore: (employees.reduce((s, e) => s + e.happiness, 0) / employees.length).toFixed(2),
      totalEmployees: employees.length,
      atRisk: employees.filter(e => e.happiness < 4.0).length
    }
  });
});

// Real-time Alerts
app.get('/api/alerts', (req, res) => {
  const allAlerts = projects.flatMap(p => 
    p.alerts.map(a => ({
      ...a,
      projectId: p.id,
      projectName: p.name,
      timestamp: new Date().toISOString()
    }))
  );
  
  res.json(allAlerts);
});

// Serve static files
app.use(express.static('/home/node/.openclaw/workspace/construction-ai-mvp/frontend'));

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Backend running on http://0.0.0.0:${PORT}`);
  console.log(`🌐 External access: http://136.110.50.115:${PORT}`);
});
