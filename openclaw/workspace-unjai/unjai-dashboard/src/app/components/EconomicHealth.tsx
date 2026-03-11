'use client';

import { motion } from 'framer-motion';

interface KPICardProps {
  icon: string;
  value: string;
  label: string;
  growth: string;
  delay: number;
}

function KPICard({ icon, value, label, growth, delay }: KPICardProps) {
  return (
    <motion.div
      style={{
        background: 'linear-gradient(135deg, #FFFBEB, #FEF3C7)',
        borderRadius: '16px',
        padding: '20px',
        border: '2px solid #FDE68A',
        boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
        position: 'relative',
        overflow: 'hidden',
      }}
      initial={{ opacity: 0, y: 20, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay, type: 'spring', stiffness: 100 }}
      whileHover={{ scale: 1.03, y: -5 }}
    >
      <motion.div
        style={{ fontSize: '40px', marginBottom: '12px' }}
        initial={{ rotate: -10, scale: 0 }}
        animate={{ rotate: 0, scale: 1 }}
        transition={{ delay: delay + 0.2, type: 'spring' }}
      >
        {icon}
      </motion.div>
      
      <motion.div
        style={{ fontSize: '24px', fontWeight: 700, color: '#B45309' }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: delay + 0.3 }}
      >
        {value}
      </motion.div>
      
      <div style={{ fontSize: '13px', color: '#92400E', marginTop: '4px' }}>{label}</div>
      
      <motion.div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          background: '#10B981',
          color: 'white',
          fontSize: '12px',
          fontWeight: 700,
          padding: '4px 12px',
          borderRadius: '20px',
          marginTop: '12px',
        }}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: delay + 0.4, type: 'spring' }}
      >
        ▲ {growth}
      </motion.div>
    </motion.div>
  );
}

export default function EconomicHealth() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* KPI Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <KPICard
          icon="🪙"
          value="2.45M"
          label="เหรียญหมุนเวียนในระบบ"
          growth="+23%"
          delay={0}
        />
        <KPICard
          icon="🎫"
          value="856K"
          label="Token ที่ใช้งานอยู่"
          growth="+18%"
          delay={0.1}
        />
      </div>
      
      {/* Blessing Pool */}
      <motion.div
        style={{
          background: 'linear-gradient(135deg, #E0F2FE, #BAE6FD)',
          border: '2px solid #7DD3FC',
          borderRadius: '16px',
          padding: '24px',
          textAlign: 'center',
          boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
          position: 'relative',
          overflow: 'hidden',
        }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, type: 'spring' }}
        whileHover={{ scale: 1.02 }}
      >
        {/* Animated background */}
        <motion.div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
          }}
          animate={{ x: ['-100%', '100%'] }}
          transition={{ duration: 3, repeat: Infinity, repeatDelay: 2 }}
        />
        
        {/* Diamond decoration */}
        <motion.div
          style={{ position: 'absolute', top: '-20px', right: '-20px', fontSize: '80px', opacity: 0.15 }}
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
        >
          💎
        </motion.div>
        
        <div style={{ position: 'relative', zIndex: 1 }}>
          <motion.div
            style={{ fontSize: '48px', marginBottom: '8px' }}
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
          >
            💎
          </motion.div>
          
          <motion.div
            style={{ fontSize: '36px', fontWeight: 700, color: '#0369A1' }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            ฿ 1,250,000
          </motion.div>
          
          <div style={{ color: '#0C4A6E', fontWeight: 500, marginTop: '4px' }}>The Blessing Pool</div>
          <div style={{ fontSize: '14px', color: '#0369A1', opacity: 0.8 }}>ยอดสนับสนุนจาก Sponsors</div>
          
          <motion.div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              background: '#10B981',
              color: 'white',
              fontSize: '14px',
              fontWeight: 700,
              padding: '8px 16px',
              borderRadius: '20px',
              marginTop: '16px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5, type: 'spring' }}
          >
            ▲ +45% จากเดือนที่แล้ว
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
