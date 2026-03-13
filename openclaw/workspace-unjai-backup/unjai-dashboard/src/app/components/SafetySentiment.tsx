'use client';

import { motion } from 'framer-motion';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';

const moodData = [
  { day: 'จ', mood: 45 },
  { day: 'อ', mood: 52 },
  { day: 'พ', mood: 48 },
  { day: 'พฤ', mood: 65 },
  { day: 'ศ', mood: 72 },
  { day: 'ส', mood: 78 },
  { day: 'อา', mood: 82 },
];

const sparklineData = [30, 45, 25, 60, 40, 35, 50];

export default function SafetySentiment() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
      {/* SOS Cases */}
      <motion.div
        style={{
          background: 'linear-gradient(135deg, #FEE2E2, #FECACA)',
          borderRadius: '16px',
          padding: '20px',
          border: '2px solid #FCA5A5',
          boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
        }}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.1 }}
        whileHover={{ scale: 1.02 }}
      >
        <div style={{ textAlign: 'center' }}>
          <div style={{ color: '#991B1B', fontWeight: 700, fontSize: '14px', marginBottom: '12px' }}>
            SOS Cases Detected
          </div>
          
          {/* Gauge */}
          <div style={{ position: 'relative', width: '100px', height: '50px', margin: '0 auto 12px' }}>
            <svg viewBox="0 0 100 50" style={{ width: '100%', height: '100%' }}>
              <path
                d="M 10 50 A 40 40 0 0 1 90 50"
                fill="none"
                stroke="rgba(255,255,255,0.5)"
                strokeWidth="10"
              />
              <motion.path
                d="M 10 50 A 40 40 0 0 1 50 10"
                fill="none"
                stroke="#EF4444"
                strokeWidth="10"
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 0.3 }}
                transition={{ delay: 0.5, duration: 1 }}
              />
            </svg>
            <motion.div
              style={{ position: 'absolute', bottom: 0, left: '50%', transform: 'translateX(-50%)', fontSize: '22px', fontWeight: 700, color: '#DC2626' }}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.7, type: 'spring' }}
            >
              12
            </motion.div>
          </div>
          
          {/* Sparkline */}
          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'center', gap: '4px', height: '40px', marginBottom: '12px' }}>
            {sparklineData.map((value, i) => (
              <motion.div
                key={i}
                style={{
                  width: '12px',
                  background: 'linear-gradient(to top, #FCA5A5, #FECACA)',
                  borderRadius: '2px 2px 0 0',
                  minHeight: '4px',
                }}
                initial={{ scaleY: 0 }}
                animate={{ scaleY: 1 }}
                transition={{ delay: 0.3 + i * 0.05 }}
              />
            ))}
          </div>
          
          <motion.div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              background: 'white',
              color: '#059669',
              fontWeight: 700,
              padding: '8px 16px',
              borderRadius: '20px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.8, type: 'spring' }}
          >
            <span>✓</span> 92% Success Rate
          </motion.div>
        </div>
      </motion.div>
      
      {/* Mood Monitoring */}
      <motion.div
        style={{
          background: 'linear-gradient(135deg, #D1FAE5, #A7F3D0)',
          borderRadius: '16px',
          padding: '20px',
          border: '2px solid #6EE7B7',
          boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
        }}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
        whileHover={{ scale: 1.02 }}
      >
        <div style={{ color: '#065F46', fontWeight: 700, fontSize: '14px', marginBottom: '12px', textAlign: 'center' }}>
          Overall Mood
        </div>
        
        {/* Mood Chart */}
        <div style={{ height: '100px', marginBottom: '8px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={moodData}>
              <defs>
                <linearGradient id="moodGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#34D399" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#34D399" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="mood"
                stroke="#10B981"
                strokeWidth={2}
                fill="url(#moodGradient)"
                animationDuration={1500}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        
        {/* Mood Emojis */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', padding: '0 8px', fontSize: '20px' }}>
          {['😔', '😐', '🙂', '😊', '🥰'].map((emoji, i) => (
            <motion.span
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + i * 0.1 }}
            >
              {emoji}
            </motion.span>
          ))}
        </div>
        
        <motion.div
          style={{
            background: 'white',
            borderRadius: '12px',
            padding: '12px',
            textAlign: 'center',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
          }}
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.6 }}
        >
          <motion.span
            style={{ fontSize: '24px', fontWeight: 700, color: '#059669' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
          >
            +72%
          </motion.span>
          <div style={{ fontSize: '12px', color: '#047857' }}>Positive Sentiment</div>
        </motion.div>
      </motion.div>
    </div>
  );
}
