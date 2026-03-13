'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';

interface ProvinceData {
  id: string;
  name: string;
  volunteers: number;
  activities: number;
  sentiment: 'high' | 'medium' | 'low';
}

const provincesData: ProvinceData[] = [
  { id: 'bangkok', name: 'กรุงเทพมหานคร', volunteers: 45, activities: 128, sentiment: 'high' },
  { id: 'chiangmai', name: 'เชียงใหม่', volunteers: 32, activities: 89, sentiment: 'high' },
  { id: 'phuket', name: 'ภูเก็ต', volunteers: 28, activities: 76, sentiment: 'high' },
  { id: 'chonburi', name: 'ชลบุรี', volunteers: 35, activities: 95, sentiment: 'high' },
  { id: 'khonkaen', name: 'ขอนแก่น', volunteers: 24, activities: 67, sentiment: 'medium' },
  { id: 'nakhonratchasima', name: 'นครราชสีมา', volunteers: 22, activities: 58, sentiment: 'medium' },
  { id: 'songkhla', name: 'สงขลา', volunteers: 19, activities: 52, sentiment: 'medium' },
  { id: 'chiangrai', name: 'เชียงราย', volunteers: 15, activities: 43, sentiment: 'medium' },
  { id: 'phitsanulok', name: 'พิษณุโลก', volunteers: 12, activities: 34, sentiment: 'low' },
  { id: 'ubon', name: 'อุบลราชธานี', volunteers: 11, activities: 31, sentiment: 'low' },
];

const getSentimentColor = (sentiment: string) => {
  switch (sentiment) {
    case 'high': return '#10B981';
    case 'medium': return '#FBBF24';
    case 'low': return '#9CA3AF';
    default: return '#9CA3AF';
  }
};

export default function ThailandMap() {
  const [hoveredProvince, setHoveredProvince] = useState<ProvinceData | null>(null);

  const provincePaths: Record<string, { path: string; name: string; x: number; y: number }> = {
    chiangmai: { path: 'M85,40 L95,35 L105,40 L110,50 L100,60 L90,55 Z', name: 'เชียงใหม่', x: 95, y: 48 },
    chiangrai: { path: 'M105,30 L120,25 L130,35 L125,45 L110,40 Z', name: 'เชียงราย', x: 118, y: 35 },
    phitsanulok: { path: 'M100,80 L115,75 L125,85 L120,95 L105,90 Z', name: 'พิษณุโลก', x: 112, y: 84 },
    khonkaen: { path: 'M140,90 L160,85 L170,95 L160,105 L140,100 Z', name: 'ขอนแก่น', x: 155, y: 94 },
    ubon: { path: 'M180,110 L200,105 L210,115 L200,125 L185,120 Z', name: 'อุบลฯ', x: 195, y: 114 },
    nakhonratchasima: { path: 'M150,130 L175,125 L185,135 L175,145 L155,140 Z', name: 'นครราชสีมา', x: 168, y: 134 },
    bangkok: { path: 'M115,160 L135,155 L145,165 L135,175 L120,170 Z', name: 'กทม.', x: 130, y: 164 },
    chonburi: { path: 'M145,165 L165,160 L175,170 L165,180 L150,175 Z', name: 'ชลบุรี', x: 160, y: 168 },
    songkhla: { path: 'M125,240 L145,235 L155,245 L145,255 L130,250 Z', name: 'สงขลา', x: 140, y: 244 },
    phuket: { path: 'M85,260 L105,255 L110,265 L100,270 L90,265 Z', name: 'ภูเก็ต', x: 98, y: 262 },
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <svg viewBox="0 0 250 300" style={{ width: '100%', height: '100%', filter: 'drop-shadow(0 8px 16px rgba(0,0,0,0.15))' }}>
        <defs>
          <linearGradient id="mapGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#E0F7FA" />
            <stop offset="50%" stopColor="#E8F5E9" />
            <stop offset="100%" stopColor="#F3E5F5" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        {/* Thailand base shape */}
        <path 
          d="M90,25 Q100,20 115,25 L130,30 Q145,35 155,45 L165,55 Q175,65 180,80 L185,95 Q190,110 195,125 L200,140 Q205,155 200,170 L195,185 Q190,200 185,215 L180,230 Q175,245 165,255 L155,265 Q145,275 130,278 L115,280 Q100,278 90,275 L80,270 Q70,265 65,255 L60,245 Q55,235 60,220 L65,205 Q70,190 75,175 L80,160 Q85,145 82,130 L78,115 Q75,100 78,85 L82,70 Q85,55 88,40 Z"
          fill="url(#mapGradient)"
          stroke="#0891B2"
          strokeWidth="2"
          opacity="0.3"
        />
        
        {/* Province markers */}
        {provincesData.map((province) => {
          const pathData = provincePaths[province.id];
          if (!pathData) return null;
          
          return (
            <g key={province.id}>
              <motion.path
                d={pathData.path}
                fill={getSentimentColor(province.sentiment)}
                stroke="white"
                strokeWidth="2"
                initial={{ scale: 1, opacity: 0.8 }}
                whileHover={{ scale: 1.2, opacity: 1 }}
                whileTap={{ scale: 0.95 }}
                onHoverStart={() => setHoveredProvince(province)}
                onHoverEnd={() => setHoveredProvince(null)}
                style={{ cursor: 'pointer' }}
              />
              {province.sentiment === 'high' && (
                <motion.circle
                  cx={pathData.x}
                  cy={pathData.y}
                  r="8"
                  fill={getSentimentColor(province.sentiment)}
                  opacity="0.3"
                  animate={{
                    scale: [1, 1.5, 1],
                    opacity: [0.3, 0.1, 0.3],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                />
              )}
            </g>
          );
        })}
        
        {/* Connection lines from hub */}
        <motion.path
          d="M130,164 L95,48 M130,164 L118,35 M130,164 L112,84 M130,164 L155,94 M130,164 L195,114 M130,164 L168,134 M130,164 L160,168 M130,164 L140,244 M130,164 L98,262"
          stroke="#67E8F9"
          strokeWidth="1"
          strokeDasharray="5,5"
          fill="none"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 0.5 }}
          transition={{ duration: 2, ease: "easeInOut" }}
        />
        
        {/* Hub marker */}
        <motion.g
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.5, type: "spring" }}
        >
          <circle
            cx="130"
            cy="164"
            r="12"
            fill="#FBBF24"
            stroke="white"
            strokeWidth="3"
            filter="url(#glow)"
          />
          <text x="130" y="168" textAnchor="middle" fontSize="12">🏠</text>
        </motion.g>
      </svg>
      
      {/* Tooltip */}
      {hoveredProvince && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            position: 'absolute',
            top: '16px',
            left: '16px',
            background: 'rgba(255,255,255,0.95)',
            backdropFilter: 'blur(8px)',
            borderRadius: '12px',
            padding: '16px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
            border: '1px solid #D1FAE5',
            zIndex: 10,
          }}
        >
          <h4 style={{ fontWeight: 700, fontSize: '16px', color: '#1F2937', marginBottom: '8px' }}>
            {hoveredProvince.name}
          </h4>
          <div style={{ fontSize: '14px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10B981' }}></span>
              <span style={{ color: '#6B7280' }}>อาสาสมัคร:</span>
              <span style={{ fontWeight: 600, color: '#059669' }}>{hoveredProvince.volunteers} คน</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#FBBF24' }}></span>
              <span style={{ color: '#6B7280' }}>กิจกรรม:</span>
              <span style={{ fontWeight: 600, color: '#D97706' }}>{hoveredProvince.activities} ครั้ง</span>
            </div>
          </div>
        </motion.div>
      )}
      
      {/* Legend */}
      <div style={{
        position: 'absolute',
        bottom: '16px',
        right: '16px',
        background: 'rgba(255,255,255,0.9)',
        backdropFilter: 'blur(4px)',
        borderRadius: '12px',
        padding: '12px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
      }}>
        <div style={{ fontSize: '12px', fontWeight: 600, color: '#6B7280', marginBottom: '8px' }}>ความคึกคัก</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#10B981' }}></div>
            <span style={{ fontSize: '12px', color: '#4B5563' }}>สูง</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#FBBF24' }}></div>
            <span style={{ fontSize: '12px', color: '#4B5563' }}>ปานกลาง</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#9CA3AF' }}></div>
            <span style={{ fontSize: '12px', color: '#4B5563' }}>เริ่มต้น</span>
          </div>
        </div>
      </div>
    </div>
  );
}
