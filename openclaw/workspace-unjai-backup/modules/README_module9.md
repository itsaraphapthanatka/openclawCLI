# Module 9: Analytics Dashboard (The Insights Engine)

## 📚 Overview

Module นี้เป็น **"ระบบวิเคราะห์และรายงาน"** ของ Nong Unjai AI รับผิดชอบ:
- **Engagement Metrics** - สถิติการใช้งานของผู้ใช้
- **Sentiment Analysis** - วิเคราะห์แนวโน้มอารมณ์
- **Crisis Detection** - รายงานเหตุการณ์วิกฤต
- **R-Score Distribution** - การกระจายคะแนนสุขภาพจิต
- **Content Performance** - ประสิทธิภาพเนื้อหา
- **ROI Reports** - รายงานผลลัพธ์สำหรับสปอนเซอร์

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│       Analytics Dashboard               │
│  (FastAPI + PostgreSQL + Redis)         │
├─────────────────────────────────────────┤
│  📊 Engagement Metrics                  │
│  💭 Sentiment Analysis                  │
│  🚨 Crisis Detection                    │
│  💚 R-Score Distribution                │
│  🎬 Content Performance                 │
│  📈 ROI Reports                         │
└─────────────────────────────────────────┘
              ↓
    Dashboard API (REST)
              ↓
    Admin Panel / Sponsors
```

## 📦 Installation

```bash
# Dependencies
pip install fastapi uvicorn psycopg2-binary redis

# Run API server
python -c "from module_9_analytics import AnalyticsDashboard, create_dashboard_api; \
           import uvicorn; \
           uvicorn.run(create_dashboard_api(AnalyticsDashboard()), host='0.0.0.0', port=8002)"
```

## 🚀 Quick Start

### 1. Initialize

```python
from module_9_analytics import AnalyticsDashboard

analytics = AnalyticsDashboard()
```

### 2. Get Dashboard Data

```python
# Full dashboard
dashboard = analytics.get_full_dashboard()

print(dashboard["engagement"])
print(dashboard["sentiment"])
print(dashboard["rscore_distribution"])
```

### 3. Run API Server

```python
from module_9_analytics import AnalyticsDashboard, create_dashboard_api
import uvicorn

analytics = AnalyticsDashboard()
app = create_dashboard_api(analytics)

uvicorn.run(app, host="0.0.0.0", port=8002)
```

## 📊 Available Metrics

### Engagement Metrics

```python
from module_9_analytics import MetricPeriod

metrics = analytics.get_engagement_metrics(MetricPeriod.TODAY)

print(metrics.total_users)        # 1000
print(metrics.active_users)       # 350
print(metrics.new_users)          # 50
print(metrics.total_messages)     # 5000
print(metrics.avg_messages_per_user)  # 14.3
```

### Sentiment Metrics

```python
sentiment = analytics.get_sentiment_metrics(MetricPeriod.WEEK)

print(sentiment.total_analyzed)   # 3500
print(sentiment.positive_count)   # 2100
print(sentiment.negative_count)   # 350
print(sentiment.trend)            # "improving"
print(sentiment.avg_sentiment_score)  # 0.45
```

### Crisis Metrics

```python
crisis = analytics.get_crisis_metrics(MetricPeriod.MONTH)

print(crisis.total_incidents)     # 25
print(crisis.emergency_count)     # 5
print(crisis.warning_count)       # 20
print(crisis.resolved_count)      # 24
print(crisis.avg_response_time)   # 2.5 minutes
print(crisis.common_triggers)     # ["อยากตาย", "ไม่ไหวแล้ว"]
```

### R-Score Distribution

```python
rscore = analytics.get_rscore_distribution()

print(rscore.to_dict())
# {
#     "distribution": {
#         "low_0_40": {"count": 100, "percentage": 10.0, "label": "needs_support"},
#         "medium_41_60": {"count": 300, "percentage": 30.0, "label": "developing"},
#         "high_61_80": {"count": 400, "percentage": 40.0, "label": "doing_well"},
#         "excellent_81_100": {"count": 200, "percentage": 20.0, "label": "ready_to_help"}
#     },
#     "average": 65.5,
#     "total_users": 1000
# }
```

### Content Metrics

```python
content = analytics.get_content_metrics(MetricPeriod.MONTH)

print(content.total_videos_watched)      # 5000
print(content.total_quizzes_completed)   # 1200
print(content.avg_quiz_score)            # 75.5
print(content.top_videos)                # [{"video_id": "v1", "views": 500}]
print(content.top_quizzes)               # [{"quiz_id": "q1", "attempts": 200}]
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/dashboard` | GET | Full dashboard data |
| `/metrics/engagement` | GET | Engagement metrics (period: today/week/month) |
| `/metrics/sentiment` | GET | Sentiment analysis |
| `/metrics/crisis` | GET | Crisis detection reports |
| `/metrics/rscore` | GET | R-score distribution |
| `/reports/roi` | GET | ROI report for sponsors |
| `/health` | GET | System health |

### Example API Calls

```bash
# Full dashboard
curl http://localhost:8002/dashboard

# Engagement metrics
curl "http://localhost:8002/metrics/engagement?period=week"

# Crisis report
curl "http://localhost:8002/metrics/crisis?period=month"

# ROI report for sponsors
curl "http://localhost:8002/reports/roi?period=quarter"
```

## 📈 ROI Report

```python
roi = analytics.get_roi_report(MetricPeriod.MONTH)

print(roi)
# {
#     "period": "month",
#     "generated_at": "2024-01-15T10:00:00",
#     "summary": {
#         "total_users_reached": 1000,
#         "active_users": 350,
#         "mental_health_improvement": 72.5,
#         "crisis_interventions": 25,
#         "crisis_prevention_rate": 96.0,
#         "content_engagement": {
#             "videos_watched": 5000,
#             "quizzes_completed": 1200
#         }
#     },
#     "r_score_distribution": {...},
#     "sentiment_breakdown": {...},
#     "key_metrics": {
#         "avg_r_score": 65.5,
#         "avg_sentiment": 0.45,
#         "user_retention": 85.7
#     }
# }
```

## 🗃️ Database Schema

```sql
-- Interaction logs
CREATE TABLE interaction_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    message TEXT,
    response_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sentiment analysis
CREATE TABLE sentiment_analysis (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    message TEXT,
    sentiment_score FLOAT,
    sentiment_label VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Crisis incidents
CREATE TABLE crisis_incidents (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    level VARCHAR(20),  -- WARNING, EMERGENCY
    trigger_keyword VARCHAR(100),
    detected_at TIMESTAMP DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    handled_by VARCHAR(255)
);

-- Video watches
CREATE TABLE video_watches (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    video_id VARCHAR(255) NOT NULL,
    watched_at TIMESTAMP DEFAULT NOW()
);

-- Quiz attempts
CREATE TABLE quiz_attempts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    quiz_id VARCHAR(255) NOT NULL,
    score FLOAT,
    completed_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_interactions_user ON interaction_logs(user_id);
CREATE INDEX idx_interactions_date ON interaction_logs(created_at);
CREATE INDEX idx_sentiment_date ON sentiment_analysis(created_at);
CREATE INDEX idx_crisis_detected ON crisis_incidents(detected_at);
```

## 🔗 Integration with Other Modules

### From Main Orchestrator (Module 3)

```python
# Log every interaction
async def process_message(self, user_id, message, session):
    # Process message...
    
    # Log to analytics
    self._log_interaction(user_id, message, response)
    
    return response

def _log_interaction(self, user_id, message, response):
    conn = self._get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO interaction_logs (user_id, message, response_type)
        VALUES (%s, %s, %s)
    """, (user_id, message, response["type"]))
    
    conn.commit()
    cursor.close()
    conn.close()
```

### From NLP Processor (Module 2)

```python
# Log sentiment analysis
def analyze(self, text):
    result = self._analyze_sentiment(text)
    
    # Save to analytics
    self._log_sentiment(user_id, text, result)
    
    return result
```

## 📊 Dashboard Visualization Ideas

```
┌─────────────────────────────────────────────────────────┐
│                    📊 Dashboard                         │
├─────────────────────────────────────────────────────────┤
│  Active Users: 350    Total Users: 1,000    New: 50    │
├─────────────────────────────────────────────────────────┤
│  Sentiment Chart       R-Score Distribution            │
│  [POS: 60%]            [■■■■░░░░░░] 40% doing_well     │
│  [NEU: 30%]            [■■■■■■░░░░] 30% developing    │
│  [NEG: 10%]            [■■■■■■■■░░] 20% ready_to_help │
│                        [■■░░░░░░░░] 10% needs_support │
├─────────────────────────────────────────────────────────┤
│  Crisis Incidents: 25    Resolved: 24 (96%)            │
│  Avg Response Time: 2.5 minutes                        │
├─────────────────────────────────────────────────────────┤
│  Top Content:                                          │
│  1. การรักตัวเอง (500 views)                           │
│  2. ความหวังในวิกฤต (450 views)                        │
└─────────────────────────────────────────────────────────┘
```

## 🧪 Testing

```bash
# Run built-in tests
python module_9_analytics.py
```

Expected output:
```
======================================================================
📊 Analytics Dashboard Test
======================================================================

📈 Dashboard Components:
   ✅ Engagement Metrics
   ✅ Sentiment Analysis
   ✅ Crisis Detection
   ✅ R-Score Distribution
   ✅ Content Performance
   ✅ System Health
   ✅ ROI Reports

🏥 Health Check:
   Status: healthy
   Modules: engagement, sentiment, crisis, rscore, content

📡 API Endpoints Available:
   GET /dashboard - Full dashboard
   GET /metrics/engagement
   GET /metrics/sentiment
   GET /metrics/crisis
   GET /metrics/rscore
   GET /reports/roi
   GET /health

✅ Analytics Dashboard initialized successfully!
```

## ⚙️ Configuration

### Environment Variables

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=unjai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword

REDIS_HOST=localhost
REDIS_PORT=6379
```

### Metric Periods

| Period | Description |
|--------|-------------|
| `today` | Last 24 hours |
| `week` | Last 7 days |
| `month` | Last 30 days |
| `quarter` | Last 90 days |
| `year` | Last 365 days |

## 👥 Agents ที่เกี่ยวข้อง

| Agent | บทบาทใน Module นี้ |
|-------|-------------------|
| **Insights Analyst** | สรุปสถิติและรายงาน |
| **System Monitor** | ตรวจสอบสถานะระบบ |

## 🔮 Future Improvements

- [ ] Real-time websocket updates
- [ ] Export to Excel/PDF
- [ ] Custom date range queries
- [ ] Cohort analysis
- [ ] Predictive analytics
- [ ] A/B test results
- [ ] User journey funnel
- [ ] Geographic distribution

## 📚 Dependencies

```
fastapi>=0.100.0
uvicorn>=0.23.0
psycopg2-binary>=2.9.9
redis>=5.0.0
```
