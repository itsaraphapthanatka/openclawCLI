'use client';

import { motion } from 'framer-motion';

interface FunnelStage {
  name: string;
  count: number;
  label: string;
  color: string;
  icon: string;
}

const funnelData: FunnelStage[] = [
  { name: 'Open Space', count: 12450, label: 'คนแปลกหน้า', color: 'linear-gradient(135deg, #C4B5FD, #A78BFA)', icon: '👤' },
  { name: 'Study Corner', count: 5280, label: 'ผู้เริ่มเติบโต', color: 'linear-gradient(135deg, #67E8F9, #22D3EE)', icon: '📖' },
  { name: 'Inner Circle', count: 2156, label: 'ครอบครัวอาสา', color: 'linear-gradient(135deg, #FBBF24, #F59E0B)', icon: '🤝' },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.2 },
  },
} as const;

const itemVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.9 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: 'spring' as const, stiffness: 100 },
  },
};

export default function UserFunnel() {
  const conversionRate = ((funnelData[2].count / funnelData[0].count) * 100).toFixed(1);
  
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}
    >
      {funnelData.map((stage, index) => (
        <motion.div
          key={stage.name}
          variants={itemVariants}
          style={{ position: 'relative' }}
        >
          <motion.div
            style={{
              background: stage.color,
              borderRadius: '16px',
              padding: '20px',
              boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
              clipPath: index === 0 
                ? 'polygon(0 0, 100% 0, 95% 100%, 5% 100%)'
                : index === 1
                ? 'polygon(5% 0, 95% 0, 90% 100%, 10% 100%)'
                : 'polygon(10% 0, 90% 0, 85% 100%, 15% 100%)',
              marginLeft: `${index * 20}px`,
              marginRight: `${index * 20}px`,
            }}
            whileHover={{ scale: 1.02, zIndex: 10 }}
            transition={{ type: 'spring', stiffness: 300 }}
          >
            {/* Floating avatars */}
            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '-8px', marginBottom: '8px' }}>
              {[...Array(Math.min(3, index + 2))].map((_, i) => (
                <motion.div
                  key={i}
                  style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '50%',
                    background: 'rgba(255,255,255,0.9)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '18px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    marginLeft: i === 0 ? 0 : '-8px',
                    border: '2px solid rgba(255,255,255,0.5)',
                  }}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.3 + i * 0.1 }}
                  whileHover={{ scale: 1.2, zIndex: 20 }}
                >
                  {stage.icon}
                </motion.div>
              ))}
              {index === 0 && (
                <motion.div
                  style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '50%',
                    background: 'rgba(255,255,255,0.8)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    fontWeight: 'bold',
                    marginLeft: '-8px',
                    border: '2px solid rgba(255,255,255,0.5)',
                  }}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.6 }}
                >
                  +
                </motion.div>
              )}
            </div>
            
            <div style={{ textAlign: 'center', color: 'white' }}>
              <motion.div
                style={{ fontSize: '28px', fontWeight: 700, textShadow: '0 2px 4px rgba(0,0,0,0.2)' }}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 + index * 0.1, type: 'spring' }}
              >
                {stage.count.toLocaleString()}
              </motion.div>
              <div style={{ fontSize: '14px', fontWeight: 500, opacity: 0.9, marginTop: '4px' }}>{stage.name}</div>
              <div style={{ fontSize: '12px', opacity: 0.75 }}>{stage.label}</div>
            </div>
          </motion.div>
          
          {/* Arrow between stages */}
          {index < funnelData.length - 1 && (
            <motion.div
              style={{ display: 'flex', justifyContent: 'center', margin: '-4px 0' }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 + index * 0.2 }}
            >
              <motion.div
                style={{ color: '#34D399', fontSize: '20px' }}
                animate={{ y: [0, 5, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                ▼
              </motion.div>
            </motion.div>
          )}
        </motion.div>
      ))}
      
      {/* Conversion Rate */}
      <motion.div
        style={{
          marginTop: '16px',
          background: 'linear-gradient(135deg, #D1FAE5, #A7F3D0)',
          borderRadius: '16px',
          padding: '20px',
          textAlign: 'center',
          border: '1px solid #6EE7B7',
          boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
        }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        whileHover={{ scale: 1.02 }}
      >
        <motion.div
          style={{ fontSize: '36px', fontWeight: 700, color: '#059669' }}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 1, type: 'spring', stiffness: 200 }}
        >
          {conversionRate}%
        </motion.div>
        <div style={{ fontSize: '14px', color: '#047857', marginTop: '4px', fontWeight: 500 }}>Conversion Rate</div>
        <div style={{ fontSize: '12px', color: '#065F46', opacity: 0.8 }}>จากแปลกหน้า → ครอบครัว</div>
      </motion.div>
    </motion.div>
  );
}
