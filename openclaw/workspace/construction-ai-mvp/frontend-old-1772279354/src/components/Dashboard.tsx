'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Building2, 
  TrendingUp, 
  AlertTriangle, 
  Users, 
  Leaf, 
  Shield,
  DollarSign,
  Activity,
  Menu,
  X
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';

// Types
interface Project {
  id: string;
  name: string;
  budget: number;
  status: string;
  riskLevel: string;
  predictedProfit: number;
  actualProfit: number | null;
  alerts: any[];
}

interface DashboardSummary {
  totalProjects: number;
  activeProjects: number;
  totalBudget: number;
  avgProfit: string;
  trafficLight: {
    green: number;
    yellow: number;
    red: number;
  };
}

// Mock data for charts
const profitForecastData = [
  { month: 'เดือน 1', predicted: 5.2, optimistic: 7.5, pessimistic: 3.0 },
  { month: 'เดือน 2', predicted: 6.8, optimistic: 9.0, pessimistic: 4.5 },
  { month: 'เดือน 3', predicted: 8.1, optimistic: 11.0, pessimistic: 5.8 },
  { month: 'เดือน 4', predicted: 9.5, optimistic: 12.5, pessimistic: 6.5 },
  { month: 'เดือน 5', predicted: 10.2, optimistic: 13.0, pessimistic: 7.2 },
  { month: 'เดือน 6', predicted: 11.5, optimistic: 14.5, pessimistic: 8.0 },
];

const esgData = [
  { name: 'สิ่งแวดล้อม', value: 85, color: '#22c55e' },
  { name: 'สังคม', value: 90, color: '#3b82f6' },
  { name: 'ธรรมาภิบาล', value: 88, color: '#8b5cf6' },
];

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [summaryRes, projectsRes] = await Promise.all([
        axios.get('/api/dashboard/summary'),
        axios.get('/api/projects')
      ]);
      setSummary(summaryRes.data);
      setProjects(projectsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'green': return 'bg-green-500';
      case 'yellow': return 'bg-yellow-500';
      case 'red': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('th-TH', {
      style: 'currency',
      currency: 'THB',
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-white shadow-lg transition-all duration-300`}>
        <div className="p-4 flex items-center justify-between">
          {sidebarOpen && (
            <div className="flex items-center space-x-2">
              <Building2 className="h-8 w-8 text-blue-600" />
              <span className="font-bold text-lg">Construction AI</span>
            </div>
          )}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-1 hover:bg-gray-100 rounded">
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
        
        <nav className="mt-6">
          {[
            { id: 'overview', label: 'ภาพรวม', icon: Activity },
            { id: 'projects', label: 'โครงการ', icon: Building2 },
            { id: 'ai-predict', label: 'AI พยากรณ์', icon: TrendingUp },
            { id: 'esg', label: 'ESG & ความยั่งยืน', icon: Leaf },
            { id: 'alerts', label: 'แจ้งเตือน', icon: AlertTriangle },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center px-4 py-3 hover:bg-gray-50 transition-colors ${
                activeTab === item.id ? 'bg-blue-50 border-r-4 border-blue-600' : ''
              }`}
            >
              <item.icon className={`h-5 w-5 ${activeTab === item.id ? 'text-blue-600' : 'text-gray-600'}`} />
              {sidebarOpen && <span className="ml-3">{item.label}</span>}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-6">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800">
            {activeTab === 'overview' && 'ภาพรวมระบบ'}
            {activeTab === 'projects' && 'รายการโครงการ'}
            {activeTab === 'ai-predict' && 'AI พยากรณ์กำไร'}
            {activeTab === 'esg' && 'ESG & ความยั่งยืน'}
            {activeTab === 'alerts' && 'ศูนย์แจ้งเตือน'}
          </h1>
          <p className="text-gray-600 mt-1">{new Date().toLocaleDateString('th-TH', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}</p>
        </header>

        {/* Overview Tab */}
        {activeTab === 'overview' && summary && (
          <div className="space-y-6">
            {/* Traffic Light Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">โครงการปกติ</p>
                    <p className="text-3xl font-bold text-green-600">{summary.trafficLight.green}</p>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
                    <Shield className="h-6 w-6 text-green-600" />
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6 border-l-4 border-yellow-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">ต้องติดตาม</p>
                    <p className="text-3xl font-bold text-yellow-600">{summary.trafficLight.yellow}</p>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-yellow-100 flex items-center justify-center">
                    <AlertTriangle className="h-6 w-6 text-yellow-600" />
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">ต้องเร่งด่วน</p>
                    <p className="text-3xl font-bold text-red-600">{summary.trafficLight.red}</p>
                  </div>
                  <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center">
                    <Activity className="h-6 w-6 text-red-600" />
                  </div>
                </div>
              </div>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow p-6">
                <p className="text-sm text-gray-600">โครงการทั้งหมด</p>
                <p className="text-2xl font-bold">{summary.totalProjects}</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <p className="text-sm text-gray-600">กำลังดำเนินการ</p>
                <p className="text-2xl font-bold">{summary.activeProjects}</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <p className="text-sm text-gray-600">งบประมาณรวม</p>
                <p className="text-2xl font-bold">{(summary.totalBudget / 1000000000).toFixed(2)}B</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <p className="text-sm text-gray-600">กำไรเฉลี่ยที่คาดการณ์</p>
                <p className="text-2xl font-bold text-green-600">{summary.avgProfit}%</p>
              </div>
            </div>

            {/* Profit Forecast Chart */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">📈 AI พยากรณ์กำไร (6 เดือน)</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={profitForecastData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="predicted" stroke="#3b82f6" strokeWidth={2} name="คาดการณ์" />
                    <Line type="monotone" dataKey="optimistic" stroke="#22c55e" strokeDasharray="5 5" name="乐观" />
                    <Line type="monotone" dataKey="pessimistic" stroke="#ef4444" strokeDasharray="5 5" name="悲观" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* Projects Tab */}
        {activeTab === 'projects' && (
          <div className="space-y-4">
            {projects.map((project) => (
              <div key={project.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`h-4 w-4 rounded-full ${getRiskColor(project.riskLevel)}`} />
                    <div>
                      <h3 className="font-semibold text-lg">{project.name}</h3>
                      <p className="text-sm text-gray-600">{project.id} • {formatCurrency(project.budget)}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">กำไรที่คาดการณ์</p>
                    <p className="text-xl font-bold text-green-600">{project.predictedProfit}%</p>
                  </div>
                </div>
                
                {project.alerts.length > 0 && (
                  <div className="mt-4 space-y-2">
                    {project.alerts.map((alert, idx) => (
                      <div key={idx} className={`p-3 rounded-lg flex items-center space-x-2 ${
                        alert.type === 'danger' ? 'bg-red-50 text-red-700' : 'bg-yellow-50 text-yellow-700'
                      }`}>
                        <AlertTriangle className="h-4 w-4" />
                        <span className="text-sm">{alert.message}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* AI Prediction Tab */}
        {activeTab === 'ai-predict' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow p-8 text-white">
              <h2 className="text-2xl font-bold mb-2">🤖 Pre-Project AI Scanner</h2>
              <p className="text-blue-100">วิเคราะห์ความเสี่ยงก่อนรับงานด้วย AI ที่เรียนรู้จากข้อมูลย้อนหลัง</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="font-semibold mb-4">ความแม่นยำของ AI</h3>
                <div className="flex items-center space-x-4">
                  <div className="h-24 w-24 rounded-full bg-green-100 flex items-center justify-center">
                    <span className="text-3xl font-bold text-green-600">88%</span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">ความแม่นยำในการทำนายกำไร</p>
                    <p className="text-sm text-gray-600 mt-1">จากการทดสอบ 1,000+ โครงการ</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="font-semibold mb-4">ตัวชี้วัดที่วิเคราะห์</h3>
                <ul className="space-y-2">
                  {['ประวัติลูกค้า', 'แนวโน้มต้นทุนวัสดุ', 'ความพร้อมของแรงงาน', 'สภาพอากาศ/Seasonal'].map((item) => (
                    <li key={item} className="flex items-center space-x-2 text-sm">
                      <div className="h-2 w-2 rounded-full bg-blue-500" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* ESG Tab */}
        {activeTab === 'esg' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-green-600 to-teal-600 rounded-lg shadow p-8 text-white">
              <h2 className="text-2xl font-bold mb-2">🌱 ESG Dashboard</h2>
              <p className="text-green-100">ติดตามความยั่งยืนสำหรับรายงาน SET</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <Leaf className="h-12 w-12 text-green-600 mx-auto mb-3" />
                <p className="text-3xl font-bold text-green-600">23</p>
                <p className="text-sm text-gray-600">ตันคาร์บอนที่ลดได้</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <Shield className="h-12 w-12 text-blue-600 mx-auto mb-3" />
                <p className="text-3xl font-bold text-blue-600">365</p>
                <p className="text-sm text-gray-600">วันไร้อุบัติเหตุ</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <Users className="h-12 w-12 text-purple-600 mx-auto mb-3" />
                <p className="text-3xl font-bold text-purple-600">4.5/5</p>
                <p className="text-sm text-gray-600">คะแนนความพึงพอใจพนักงาน</p>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">ESG Score โดยรวม</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={esgData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {esgData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && (
          <div className="space-y-4">
            {projects.flatMap(p => 
              p.alerts.map((alert, idx) => ({
                ...alert,
                projectId: p.id,
                projectName: p.name,
                key: `${p.id}-${idx}`
              }))
            ).map((alert) => (
              <div 
                key={alert.key} 
                className={`rounded-lg shadow p-4 ${
                  alert.type === 'danger' ? 'bg-red-50 border-l-4 border-red-500' : 'bg-yellow-50 border-l-4 border-yellow-500'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <AlertTriangle className={`h-5 w-5 ${alert.type === 'danger' ? 'text-red-600' : 'text-yellow-600'}`} />
                  <div className="flex-1">
                    <p className="font-semibold">{alert.projectName}</p>
                    <p className="text-sm mt-1">{alert.message}</p>
                    <p className="text-xs text-gray-500 mt-2">{alert.timestamp}</p>
                  </div>
                </div>
              </div>
            ))}
            
            {projects.flatMap(p => p.alerts).length === 0 && (
              <div className="text-center py-12">
                <Shield className="h-16 w-16 text-green-500 mx-auto mb-4" />
                <p className="text-lg text-gray-600">ไม่มีการแจ้งเตือนในขณะนี้</p>
                <p className="text-sm text-gray-500">ทุกโครงการดำเนินไปตามแผน</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
