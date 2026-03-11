'use client';

import { motion } from 'framer-motion';
import ThailandMap from './components/ThailandMap';
import UserFunnel from './components/UserFunnel';
import EconomicHealth from './components/EconomicHealth';
import SafetySentiment from './components/SafetySentiment';

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #E0F7FA 0%, #E8F5E9 50%, #F3E5F5 100%)',
    padding: '24px',
  },
  header: {
    textAlign: 'center' as const,
    marginBottom: '32px',
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: 700,
    background: 'linear-gradient(135deg, #059669, #0891B2)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    marginBottom: '8px',
  },
  subtitle: {
    color: '#6B7280',
    fontSize: '1rem',
  },
  date: {
    color: '#9CA3AF',
    fontSize: '0.875rem',
    marginTop: '4px',
  },
  grid: {
    maxWidth: '1400px',
    margin: '0 auto',
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))',
    gap: '24px',
  },
  card: {
    background: 'rgba(255, 255, 255, 0.85)',
    backdropFilter: 'blur(12px)',
    borderRadius: '24px',
    padding: '24px',
    boxShadow: '0 8px 32px rgba(0,0,0,0.08), 0 0 0 1px rgba(255,255,255,0.5) inset',
    border: '1px solid rgba(255,255,255,0.6)',
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '20px',
    paddingBottom: '16px',
    borderBottom: '2px solid #E5E7EB',
  },
  cardIcon: {
    width: '48px',
    height: '48px',
    borderRadius: '14px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '24px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  },
  cardTitle: {
    fontSize: '1.25rem',
    fontWeight: 700,
    color: '#1F2937',
  },
  centerColumn: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '24px',
  },
  mapContainer: {
    height: '320px',
    position: 'relative' as const,
  },
  summaryBox: {
    marginTop: '16px',
    background: 'linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)',
    borderRadius: '16px',
    padding: '16px',
    border: '1px solid #6EE7B7',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
  },
  volunteersBox: {
    marginTop: '16px',
    background: 'linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)',
    borderRadius: '16px',
    padding: '16px',
    border: '1px solid #FCD34D',
  },
  footer: {
    textAlign: 'center' as const,
    marginTop: '48px',
    color: '#9CA3AF',
    fontSize: '0.875rem',
  },
};

export default function Dashboard() {
  const currentDate = new Date().toLocaleDateString('th-TH', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div style={styles.container}>
      {/* Header */}
      <motion.header
        style={styles.header}
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <motion.h1
          style={styles.title}
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring' }}
        >
          🌟 ระบบนิเวศน์น้องอุ่นใจ
        </motion.h1>
        <p style={styles.subtitle}>Ecosystem Health Dashboard</p>
        <p style={styles.date}>ภาพรวมสุขภาพระบบและการตัดสินใจเชิงกลยุทธ์ | ณ วันที่ {currentDate}</p>
      </motion.header>

      {/* Main Grid */}
      <div style={styles.grid}>
        {/* Left Column - User Funnel */}
        <motion.div
          style={styles.card}
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          <div style={{...styles.cardHeader, borderBottomColor: '#DDD6FE'}}>
            <motion.div
              style={{...styles.cardIcon, background: 'linear-gradient(135deg, #C4B5FD, #A78BFA)'}}
              whileHover={{ rotate: 10, scale: 1.1 }}
            >
              👥
            </motion.div>
            <h2 style={styles.cardTitle}>User Growth & Funnel</h2>
          </div>
          <UserFunnel />
        </motion.div>

        {/* Center Column - Economic & Safety */}
        <div style={styles.centerColumn}>
          {/* Economic Health */}
          <motion.div
            style={styles.card}
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
          >
            <div style={{...styles.cardHeader, borderBottomColor: '#FDE68A'}}>
              <motion.div
                style={{...styles.cardIcon, background: 'linear-gradient(135deg, #FDE68A, #FBBF24)'}}
                whileHover={{ rotate: 10, scale: 1.1 }}
              >
                💰
              </motion.div>
              <h2 style={styles.cardTitle}>Economic Health</h2>
            </div>
            <EconomicHealth />
          </motion.div>

          {/* Safety & Sentiment */}
          <motion.div
            style={styles.card}
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            <div style={{...styles.cardHeader, borderBottomColor: '#FECACA'}}>
              <motion.div
                style={{...styles.cardIcon, background: 'linear-gradient(135deg, #FECACA, #FCA5A5)'}}
                whileHover={{ rotate: 10, scale: 1.1 }}
              >
                🛡️
              </motion.div>
              <h2 style={styles.cardTitle}>Safety & Sentiment</h2>
            </div>
            <SafetySentiment />
          </motion.div>
        </div>

        {/* Right Column - Map */}
        <motion.div
          style={styles.card}
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          <div style={{...styles.cardHeader, borderBottomColor: '#A5F3FC'}}>
            <motion.div
              style={{...styles.cardIcon, background: 'linear-gradient(135deg, #67E8F9, #22D3EE)'}}
              whileHover={{ rotate: 10, scale: 1.1 }}
            >
              🗺️
            </motion.div>
            <h2 style={styles.cardTitle}>Geographic Impact</h2>
          </div>
          
          {/* Map Container */}
          <div style={styles.mapContainer}>
            <ThailandMap />
          </div>

          {/* Active Zones Summary */}
          <motion.div
            style={styles.summaryBox}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.8 }}
            whileHover={{ scale: 1.02 }}
          >
            <motion.span
              style={{ fontSize: '28px' }}
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              ✅
            </motion.span>
            <div>
              <div style={{ fontSize: '28px', fontWeight: 700, color: '#059669' }}>77/77</div>
              <div style={{ fontSize: '14px', color: '#047857' }}>Provinces Active</div>
            </div>
          </motion.div>

          {/* Volunteers */}
          <motion.div
            style={styles.volunteersBox}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.9 }}
          >
            <div style={{ textAlign: 'center', marginBottom: '12px' }}>
              <div style={{ fontSize: '14px', color: '#92400E', fontWeight: 500 }}>👥 อาสาสมัครที่พร้อมช่วยเหลือ</div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '12px' }}>
              {['👨', '👩', '👨', '👩'].map((avatar, i) => (
                <motion.div
                  key={i}
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: 'white',
                    border: '2px solid #FBBF24',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '20px',
                    marginLeft: i === 0 ? 0 : '-10px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  }}
                  initial={{ scale: 0, x: -20 }}
                  animate={{ scale: 1, x: 0 }}
                  transition={{ delay: 1 + i * 0.1, type: 'spring' }}
                  whileHover={{ scale: 1.2, zIndex: 10 }}
                >
                  {avatar}
                </motion.div>
              ))}
              <motion.div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: '#FBBF24',
                  color: 'white',
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '12px',
                  marginLeft: '-10px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                }}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 1.4, type: 'spring' }}
              >
                +247
              </motion.div>
            </div>
            <motion.div
              style={{ textAlign: 'center', fontSize: '24px', fontWeight: 700, color: '#B45309' }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.5 }}
            >
              251 อาสา
            </motion.div>
          </motion.div>
        </motion.div>
      </div>

      {/* Footer */}
      <motion.footer
        style={styles.footer}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
      >
        <p>🌟 ระบบนิเวศน์น้องอุ่นใจ | Nong Unjai Ecosystem Dashboard</p>
        <p style={{ marginTop: '4px' }}>สะท้อนความรักของพระเจ้าผ่านโลกดิจิทัล</p>
      </motion.footer>
    </div>
  );
}
