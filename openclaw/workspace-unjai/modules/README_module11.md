# Module 11: Trend Predictor (The Early Warning System)

## 📚 Overview

Module นี้เป็น **"ระบบวิเคราะห์และคาดการณ์แนวโน้ม"** ของ Nong Unjai AI รับผิดชอบ:
- **Keyword Trend Detection** - ตรวจจับ keyword ที่เพิ่มขึ้นผิดปกติ
- **Sentiment Trend Analysis** - วิเคราะห์แนวโน้มอารมณ์
- **Crisis Pattern Detection** - ตรวจจับรูปแบบวิกฤต
- **Predictions** - คาดการณ์สถานการณ์ล่วงหน้า

## 🎯 Use Cases

- ตรวจจับ keyword "อยากตาย" เพิ่มขึ้น 3x → Alert ทีมอาสา
- Negative sentiment เพิ่มขึ้น 50% → ส่ง content หนุนใจ
- Crisis incidents เพิ่มขึ้น → เพิ่ม volunteer ตอบแชท

## 📊 Trend Types

| Type | คำอธิบาย | Alert Level |
|------|----------|-------------|
| KEYWORD | Keyword frequency | INFO → CRITICAL |
| SENTIMENT | Emotional trends | WARNING |
| CRISIS | Crisis pattern | CRITICAL |
| CONTENT | Content popularity | INFO |
| USER_BEHAVIOR | Usage patterns | INFO |

## 🚀 Quick Start

### 1. Initialize

```python
from module_11_trend_predictor import TrendPredictor

predictor = TrendPredictor()
```

### 2. Run Analysis

```python
# Analyze last 24 hours
report = predictor.analyze_trends(hours=24)

# Print report
predictor.print_report(report)
```

### 3. Check Specific Trends

```python
# Keyword trends
keyword_trends = predictor.detect_keyword_trends(hours=24)

# Crisis trends
crisis_trends = predictor.detect_crisis_trends(hours=24)

# Sentiment trends
sentiment_trends = predictor.detect_sentiment_trends(hours=24)
```

## 📈 Thresholds

```python
RISING_THRESHOLD = 1.5   # 50% increase → Alert
SPIKE_THRESHOLD = 3.0    # 3x increase → CRITICAL
FALLING_THRESHOLD = 0.7  # 30% decrease
MIN_SAMPLES = 5          # Minimum data points
```

## 🔍 Monitored Keywords

### Crisis Keywords (12 words)
```python
["อยากตาย", "ไม่อยากอยู่", "ฆ่าตัวตาย", "ไม่ไหวแล้ว",
 "มืดแปดด้าน", "ไม่มีทางออก", "ไม่เหลืออะไร", "ทรมาน",
 "ไร้ค่า", "ไม่มีความหมาย", "ลาก่อน"]
```

### Emotional Keywords
```python
{
    "positive": ["มีความสุข", "ดีใจ", "ยิ้ม", "สบายใจ"],
    "negative": ["เศร้า", "นอย", "เหนื่อย", "ท้อ", "กังวล"],
    "angry": ["โกรธ", "แค้น", "โมโห", "หงุดหงิด"],
    "hopeful": ["หวัง", "เชื่อ", "ไว้ใจ", "ศรัทธา"]
}
```

## 📊 Sample Report

```
======================================================================
📈 Trend Analysis Report
======================================================================
Report ID: TREND-20240227-103000
Period: 24h
Generated: 2024-02-27 10:30:00

Summary:
  Total Trends: 5
  🚨 Critical: 1
  ⚠️  Warnings: 2
  ℹ️  Info: 2
  🔥 Top Rising: อยากตาย, เศร้า, ไม่ไหว

Detected Trends:

  🚨 อยากตาย
     📈 +250% (24h)
     Confidence: 80%
     → URGENT: Review crisis detection sensitivity

  ⚠️  negative_sentiment
     📈 +65% (24h)
     Confidence: 70%
     → Prepare more positive/healing content

  ⚠️  crisis_emergency
     📈 +150% (24h)
     Confidence: 75%
     → Consider increasing human volunteer monitoring

🔮 Predictions:
  • Crisis incidents increasing - prepare volunteer team
    (Confidence: 75%, 24-48 hours)
  • Community mood declining - deploy uplifting content
    (Confidence: 70%, immediate)
======================================================================
```

## 🔔 Alert Levels

| Level | Trigger | Action |
|-------|---------|--------|
| **INFO** | Normal increase | Monitor |
| **WARNING** | 50%+ increase | Prepare content |
| **CRITICAL** | Crisis keyword spike | Alert volunteers |

## 🔗 Integration

### Daily Report

```python
# Run daily at 9 AM
async def daily_trend_check():
    report = predictor.analyze_trends(hours=24)
    
    # Send to admin if critical trends found
    critical = [t for t in report.trends if t.alert_level == "critical"]
    
    if critical:
        await send_alert_to_admin(critical)
    
    # Save report
    predictor.generate_report_file(report)
```

### Real-time Monitoring

```python
# Check every hour
async def hourly_check():
    crisis_trends = predictor.detect_crisis_trends(hours=1)
    
    for trend in crisis_trends:
        if trend.alert_level == "critical":
            await trigger_volunteer_alert(trend)
```

## 📈 Trend Directions

| Direction | Icon | Description |
|-----------|------|-------------|
| RISING | 📈 | Steady increase |
| FALLING | 📉 | Decreasing |
| STABLE | ➡️ | No significant change |
| SPIKE | 🚀 | Sudden large increase |
| DROP | 💥 | Sudden decrease |

## 👥 Agents ที่เกี่ยวข้อง

| Agent | บทบาทใน Module นี้ |
|-------|-------------------|
| **Trend Predictor** | วิเคราะห์แนวโน้ม |
| **CCO** | รับ Alert และจัดการ |

## 📚 Dependencies

```
numpy>=1.24.0
psycopg2-binary>=2.9.9
```
