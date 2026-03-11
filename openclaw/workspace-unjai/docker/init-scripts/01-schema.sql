-- Nong Unjai AI Database Schema
-- Run this script to initialize the PostgreSQL database

-- ==========================================
-- User Sessions
-- ==========================================
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    nickname VARCHAR(100),
    current_persona INTEGER DEFAULT 6,
    current_circle INTEGER DEFAULT 1,
    r_score FLOAT DEFAULT 50.0,
    is_new_user BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);

-- ==========================================
-- Interaction Logs
-- ==========================================
CREATE TABLE IF NOT EXISTS interaction_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    content TEXT,
    response_type VARCHAR(50),
    persona_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_interactions_user ON interaction_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_date ON interaction_logs(created_at);

-- ==========================================
-- Sentiment Analysis
-- ==========================================
CREATE TABLE IF NOT EXISTS sentiment_analysis (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    message TEXT,
    sentiment_score FLOAT,
    sentiment_label VARCHAR(20),
    r_score_delta FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sentiment_user ON sentiment_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_date ON sentiment_analysis(created_at);

-- ==========================================
-- Crisis Incidents
-- ==========================================
CREATE TABLE IF NOT EXISTS crisis_incidents (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    level VARCHAR(20),  -- WARNING, EMERGENCY
    trigger_keyword VARCHAR(100),
    detected_at TIMESTAMP DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    handled_by VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_crisis_user ON crisis_incidents(user_id);
CREATE INDEX IF NOT EXISTS idx_crisis_detected ON crisis_incidents(detected_at);

-- ==========================================
-- Coin Balances
-- ==========================================
CREATE TABLE IF NOT EXISTS user_coin_balances (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    balance INTEGER DEFAULT 0,
    lifetime_earned INTEGER DEFAULT 0,
    lifetime_spent INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_coin_balance_user ON user_coin_balances(user_id);

-- ==========================================
-- Coin Transactions
-- ==========================================
CREATE TABLE IF NOT EXISTS coin_transactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    type VARCHAR(20) NOT NULL,  -- EARN, SPEND
    amount INTEGER NOT NULL,
    reason VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transactions_user ON coin_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON coin_transactions(created_at);

-- ==========================================
-- Video Watches
-- ==========================================
CREATE TABLE IF NOT EXISTS video_watches (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    video_id VARCHAR(255) NOT NULL,
    watched_at TIMESTAMP DEFAULT NOW(),
    completed BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_video_user ON video_watches(user_id);
CREATE INDEX IF NOT EXISTS idx_video_id ON video_watches(video_id);

-- ==========================================
-- Quiz Attempts
-- ==========================================
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    quiz_id VARCHAR(255) NOT NULL,
    score FLOAT,
    completed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quiz_user ON quiz_attempts(user_id);

-- ==========================================
-- Nudge States
-- ==========================================
CREATE TABLE IF NOT EXISTS user_nudge_states (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    last_active_at TIMESTAMP DEFAULT NOW(),
    last_nudged_at TIMESTAMP,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    total_logins INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_nudge_user ON user_nudge_states(user_id);

-- ==========================================
-- Nudge History
-- ==========================================
CREATE TABLE IF NOT EXISTS nudge_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    nudge_type VARCHAR(50),
    content TEXT,
    sent_at TIMESTAMP DEFAULT NOW(),
    opened BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_nudge_history_user ON nudge_history(user_id);

-- ==========================================
-- Vector Metadata
-- ==========================================
CREATE TABLE IF NOT EXISTS vector_metadata (
    id SERIAL PRIMARY KEY,
    vector_id VARCHAR(255) NOT NULL UNIQUE,
    content TEXT,
    source_type VARCHAR(50),
    source_id VARCHAR(255),
    circle_tag VARCHAR(20),
    topic_tags TEXT[],
    scripture_refs TEXT[],
    video_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vector_circle ON vector_metadata(circle_tag);
CREATE INDEX IF NOT EXISTS idx_vector_topics ON vector_metadata USING GIN(topic_tags);

-- ==========================================
-- Insert Default Daily Verses
-- ==========================================
INSERT INTO vector_metadata (vector_id, content, source_type, circle_tag, scripture_refs) VALUES
('verse-001', 'เพราะพระเจ้าทรงรักโลก ถึงกับทรงประทานพระบุตรองค์เดียวของพระองค์...', 'daily_verse', 'SELF', ARRAY['ยอห์น 3:16']),
('verse-002', 'ข้าพเจ้าทำสิ่งสารพัดได้โดยพระองค์ผู้ทรงเสริมกำลังข้าพเจ้า...', 'daily_verse', 'SELF', ARRAY['ฟิลิปปี 4:13']),
('verse-003', 'สันติสุขที่เราฝากไว้กับเจ้า เราให้สันติสุขแก่เจ้า...', 'daily_verse', 'SELF', ARRAY['ยอห์น 14:27']),
('verse-004', 'เรารู้ว่าสิ่งสารพัดร่วมมือกันให้เกิดผลดี...', 'daily_verse', 'SELF', ARRAY['โรม 8:28']),
('verse-005', 'พระเยโฮวาห์ทรงเป็นผู้เลี้ยงดูของข้าพเจ้า...', 'daily_verse', 'SELF', ARRAY['สดุดี 23:1'])
ON CONFLICT (vector_id) DO NOTHING;

-- ==========================================
-- Create Functions
-- ==========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ==========================================
-- Create Triggers
-- ==========================================
DROP TRIGGER IF EXISTS update_user_sessions ON user_sessions;
CREATE TRIGGER update_user_sessions
    BEFORE UPDATE ON user_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_coin_balances ON user_coin_balances;
CREATE TRIGGER update_coin_balances
    BEFORE UPDATE ON user_coin_balances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_nudge_states ON user_nudge_states;
CREATE TRIGGER update_nudge_states
    BEFORE UPDATE ON user_nudge_states
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
