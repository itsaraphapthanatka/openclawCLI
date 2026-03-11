'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';
import axios from 'axios';

interface Project {
  id: string;
  name: string;
  budget: number;
  predictedProfit: number;
  riskLevel: 'green' | 'yellow' | 'red';
  alerts: string[];
  location: string;
  startDate: string;
  progress: number;
}

const projects: Project[] = [
  { id: 'PROJ-001', name: 'คอนโด High-Rise สุขุมวิท', budget: 500000000, predictedProfit: 12.5, riskLevel: 'green', alerts: [], location: 'กรุงเทพฯ', startDate: '2024-01-15', progress: 75 },
  { id: 'PROJ-002', name: 'โรงงาน EEC ระยอง', budget: 800000000, predictedProfit: 8.2, riskLevel: 'yellow', alerts: ['ต้นทุนวัสดุเพิ่ม 5%'], location: 'ระยอง', startDate: '2024-02-01', progress: 45 },
  { id: 'PROJ-003', name: 'โรงพยาบาลเชียงใหม่', budget: 1200000000, predictedProfit: 3.5, riskLevel: 'red', alerts: ['กำลังคนไม่พอ', 'Client จ่ายช้า'], location: 'เชียงใหม่', startDate: '2024-03-01', progress: 20 },
];

const forecastData = [
  { month: 'ม.ค.', profit: 5.2, target: 5.0 },
  { month: 'ก.พ.', profit: 6.5, target: 6.0 },
  { month: 'มี.ค.', profit: 7.8, target: 7.5 },
  { month: 'เม.ย.', profit: 9.1, target: 9.0 },
  { month: 'พ.ค.', profit: 10.5, target: 10.0 },
  { month: 'มิ.ย.', profit: 11.8, target: 11.5 },
];

const budgetData = [
  { name: 'คอนโดสุขุมวิท', value: 500, color: '#6366f1' },
  { name: 'โรงงานระยอง', value: 800, color: '#f59e0b' },
  { name: 'โรงพยาบาล', value: 1200, color: '#ec4899' },
];

const monthlyData = [
  { month: 'ม.ค.', income: 45, expense: 38 },
  { month: 'ก.พ.', income: 52, expense: 41 },
  { month: 'มี.ค.', income: 48, expense: 45 },
  { month: 'เม.ย.', income: 61, expense: 50 },
  { month: 'พ.ค.', income: 58, expense: 48 },
  { month: 'มิ.ย.', income: 67, expense: 52 },
];

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      const response = await axios.get('http://localhost:3001/api/dashboard/summary');
      setSummary(response.data);
    } catch (error) {
      setSummary({ totalProjects: 3, activeProjects: 2, totalBudget: 2500000000, avgProfit: '8.07', trafficLight: { green: 1, yellow: 1, red: 1 } });
    }
    setLoading(false);
  };

  if (loading || !summary) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-20 w-20 border-4 border-indigo-500 border-t-transparent"></div>
      </div>
    );
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'green': return { bg: 'bg-emerald-500', light: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30' };
      case 'yellow': return { bg: 'bg-amber-500', light: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30' };
      case 'red': return { bg: 'bg-rose-500', light: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/30' };
      default: return { bg: 'bg-slate-500', light: 'bg-slate-500/10', text: 'text-slate-400', border: 'border-slate-500/30' };
    }
  };

  const formatCurrency = (value: number) => value >= 1e9 ? `${(value / 1e9).toFixed(1)}B` : `${(value / 1e6).toFixed(0)}M`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white">
      {/* Glass Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-slate-900/80 border-b border-white/10">
        <div className="px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="h-12 w-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-indigo-500/30">
                AI
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Construction Intelligence</h1>
                <p className="text-sm text-white/50">ระบบ AI บริหารโครงการก่อสร้าง</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold">
                ไข่
              </div>
              <div>
                <div className="text-sm font-medium text-white">ไข่เป็ด 🐣</div>
                <div className="text-xs text-white/50">Administrator</div>
              </div>
            </div>
          </div>
        </div>

        <div className="px-8">
          <div className="flex space-x-1">
            {['dashboard', 'projects', 'ai', 'esg'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-4 text-sm font-medium transition-all ${
                  activeTab === tab ? 'text-white border-b-2 border-indigo-500' : 'text-white/40 hover:text-white/70'
                }`}
              >
                {tab === 'dashboard' && '📊 ภาพรวม'}
                {tab === 'projects' && '🏗️ โครงการ'}
                {tab === 'ai' && '🤖 AI Analytics'}
                {tab === 'esg' && '🌱 ESG'}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="p-8">
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            {/* Traffic Light Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { level: 'green', label: 'โครงการปกติ', count: summary.trafficLight.green, icon: '✓' },
                { level: 'yellow', label: 'ต้องติดตาม', count: summary.trafficLight.yellow, icon: '⚠' },
                { level: 'red', label: 'ต้องเร่งด่วน', count: summary.trafficLight.red, icon: '⚡' },
              ].map((item) => {
                const colors = getRiskColor(item.level);
                return (
                  <div key={item.level} className={`rounded-2xl bg-white/5 border ${colors.border} p-6 backdrop-blur-sm hover:bg-white/10 transition-all`}>
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-white/60 text-sm mb-1">{item.label}</p>
                        <p className={`text-5xl font-bold ${colors.text}`}>{item.count}</p>
                      </div>
                      <div className={`h-14 w-14 ${colors.light} rounded-2xl flex items-center justify-center text-2xl`}>{item.icon}</div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'โครงการทั้งหมด', value: summary.totalProjects, unit: 'โครงการ', change: '+12%' },
                { label: 'กำลังดำเนินการ', value: summary.activeProjects, unit: 'โครงการ', change: '+5%' },
                { label: 'งบประมาณรวม', value: formatCurrency(summary.totalBudget), unit: 'บาท', change: '+8%' },
                { label: 'กำไรเฉลี่ย', value: summary.avgProfit, unit: '%', change: '+2.3%' },
              ].map((stat, idx) => (
                <div key={idx} className="rounded-2xl bg-white/5 border border-white/10 p-5 hover:bg-white/10 transition-all">
                  <p className="text-white/50 text-sm">{stat.label}</p>
                  <p className="text-2xl font-bold text-white mt-1">{stat.value}</p>
                  <p className="text-emerald-400 text-xs">{stat.change}</p>
                </div>
              ))}
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 rounded-2xl bg-white/5 border border-white/10 p-6">
                <h3 className="text-lg font-bold text-white mb-4">📈 AI Profit Forecast</h3>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={forecastData}>
                      <defs>
                        <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                          <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="month" stroke="#ffffff30" tick={{ fill: '#ffffff60' }} />
                      <YAxis stroke="#ffffff30" tick={{ fill: '#ffffff60' }} unit="%" />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
                      <Area type="monotone" dataKey="profit" stroke="#6366f1" strokeWidth={3} fill="url(#colorProfit)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="rounded-2xl bg-white/5 border border-white/10 p-6">
                <h3 className="text-lg font-bold text-white mb-4">💰 งบประมาณ</h3>
                <div className="h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={budgetData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={8} dataKey="value">
                        {budgetData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Income/Expense Chart */}
            <div className="rounded-2xl bg-white/5 border border-white/10 p-6">
              <h3 className="text-lg font-bold text-white mb-4">💵 รายรับ - รายจ่าย</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyData}>
                    <XAxis dataKey="month" stroke="#ffffff30" tick={{ fill: '#ffffff60' }} />
                    <YAxis stroke="#ffffff30" tick={{ fill: '#ffffff60' }} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
                    <Bar dataKey="income" fill="#6366f1" radius={[8, 8, 0, 0]} />
                    <Bar dataKey="expense" fill="#ef4444" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'projects' && (
          <div className="space-y-4">
            {projects.map((project) => {
              const colors = getRiskColor(project.riskLevel);
              return (
                <div key={project.id} className="rounded-2xl bg-white/5 border border-white/10 p-6 hover:bg-white/10 transition-all">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`w-4 h-4 rounded-full ${colors.bg}`}></div>
                      <div>
                        <h4 className="text-lg font-semibold text-white">{project.name}</h4>
                        <p className="text-sm text-white/50">{project.location} • {formatCurrency(project.budget)} บาท</p>
                        <div className="mt-2 w-64">
                          <div className="flex justify-between text-xs text-white/40 mb-1">
                            <span>ความคืบหน้า</span>
                            <span>{project.progress}%</span>
                          </div>
                          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                            <div className={`h-full ${colors.bg} rounded-full`} style={{ width: `${project.progress}%` }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`px-3 py-1 rounded-full text-sm ${colors.light} ${colors.text}`}>
                        {project.riskLevel === 'green' ? 'ปกติ' : project.riskLevel === 'yellow' ? 'ติดตาม' : 'เร่งด่วน'}
                      </span>
                      <p className="text-xl font-bold text-emerald-400 mt-1">{project.predictedProfit}%</p>
                    </div>
                  </div>
                  {project.alerts.length > 0 && (
                    <div className="mt-4 space-y-2">
                      {project.alerts.map((alert, index) => (
                        <div key={index} className={`p-3 rounded-lg text-sm ${colors.light} ${colors.text}`}>⚠️ {alert}</div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {activeTab === 'ai' && (
          <div className="space-y-6">
            <div className="rounded-3xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 p-10">
              <div className="flex items-center space-x-6 mb-6">
                <div className="w-20 h-20 bg-white/20 rounded-2xl flex items-center justify-center text-4xl">🤖</div>
                <div>
                  <h2 className="text-4xl font-bold text-white mb-2">Pre-Project AI Scanner</h2>
                  <p className="text-white/80 text-lg">วิเคราะห์ความเสี่ยงก่อนรับงานด้วย AI</p>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-8">
                <div className="bg-white/10 rounded-2xl p-6">
                  <p className="text-5xl font-bold text-white">88%</p>
                  <p className="text-white/70">ความแม่นยำ</p>
                </div>
                <div className="bg-white/10 rounded-2xl p-6">
                  <p className="text-5xl font-bold text-white">1,000+</p>
                  <p className="text-white/70">โครงการที่วิเคราะห์</p>
                </div>
                <div className="bg-white/10 rounded-2xl p-6">
                  <p className="text-5xl font-bold text-white">24h</p>
                  <p className="text-white/70">เวลาประเมิน</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'esg' && (
          <div className="space-y-6">
            <div className="rounded-3xl bg-gradient-to-r from-green-600 to-teal-600 p-10">
              <h2 className="text-4xl font-bold text-white mb-2">🌱 ESG Dashboard</h2>
              <p className="text-green-100 text-lg">ติดตามความยั่งยืนสำหรับรายงาน SET</p>
            </div>
            <div className="grid grid-cols-3 gap-6">
              <div className="rounded-2xl bg-white/5 border border-white/10 p-8 text-center">
                <p className="text-5xl font-bold text-emerald-400">23</p>
                <p className="text-white/50 mt-2">ตันคาร์บอนลดได้</p>
              </div>
              <div className="rounded-2xl bg-white/5 border border-white/10 p-8 text-center">
                <p className="text-5xl font-bold text-blue-400">365</p>
                <p className="text-white/50 mt-2">วันไร้อุบัติเหตุ</p>
              </div>
              <div className="rounded-2xl bg-white/5 border border-white/10 p-8 text-center">
                <p className="text-5xl font-bold text-purple-400">4.5/5</p>
                <p className="text-white/50 mt-2">ความพึงพอใจพนักงาน</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
