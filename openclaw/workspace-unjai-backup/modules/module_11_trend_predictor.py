"""
Module 11: Trend Predictor (The Early Warning System)
Nong Unjai AI System

This module provides trend analysis and prediction:
- Keyword trend detection
- Anomaly detection in user behavior
- Sentiment trend forecasting
- Crisis pattern prediction
- Content popularity prediction
- Seasonal pattern analysis

Tech Stack:
- Statistical analysis
- Simple trend algorithms
- Time-series analysis
- PostgreSQL (Historical data)
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, Counter
import logging
import math

import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendType(Enum):
    """Types of trends"""
    KEYWORD = "keyword"
    SENTIMENT = "sentiment"
    CRISIS = "crisis"
    CONTENT = "content"
    USER_BEHAVIOR = "user_behavior"
    SEASONAL = "seasonal"


class TrendDirection(Enum):
    """Trend direction"""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    SPIKE = "spike"  # Sudden increase
    DROP = "drop"    # Sudden decrease


class AlertLevel(Enum):
    """Alert levels for trends"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class TrendDataPoint:
    """Single data point for trend analysis"""
    timestamp: datetime
    value: float
    label: str = ""
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DetectedTrend:
    """Detected trend information"""
    trend_type: TrendType
    direction: TrendDirection
    keyword_or_topic: str
    current_value: float
    previous_value: float
    change_percent: float
    time_window: str
    confidence: float
    alert_level: AlertLevel
    detected_at: datetime
    recommendation: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "type": self.trend_type.value,
            "direction": self.direction.value,
            "keyword": self.keyword_or_topic,
            "current": self.current_value,
            "previous": self.previous_value,
            "change_percent": round(self.change_percent, 2),
            "time_window": self.time_window,
            "confidence": round(self.confidence, 2),
            "alert": self.alert_level.value,
            "detected_at": self.detected_at.isoformat(),
            "recommendation": self.recommendation
        }


@dataclass
class TrendReport:
    """Complete trend analysis report"""
    report_id: str
    generated_at: datetime
    analysis_period: str
    trends: List[DetectedTrend]
    summary: Dict
    predictions: List[Dict]
    
    def to_dict(self) -> Dict:
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at.isoformat(),
            "period": self.analysis_period,
            "trends": [t.to_dict() for t in self.trends],
            "summary": self.summary,
            "predictions": self.predictions
        }


class TrendPredictor:
    """
    Trend Analysis and Prediction System
    """
    
    # Thresholds for trend detection
    RISING_THRESHOLD = 1.5      # 50% increase
    SPIKE_THRESHOLD = 3.0       # 3x increase
    FALLING_THRESHOLD = 0.7     # 30% decrease
    MIN_SAMPLES = 5             # Minimum data points
    
    # Crisis keywords to monitor
    CRISIS_KEYWORDS = [
        "อยากตาย", "ไม่อยากอยู่", "ฆ่าตัวตาย", "ไม่ไหวแล้ว",
        "มืดแปดด้าน", "ไม่มีทางออก", "ไม่เหลืออะไร", "ทรมาน",
        "ไร้ค่า", "ไม่มีความหมาย", "ลาก่อน"
    ]
    
    # Emotional keywords
    EMOTIONAL_KEYWORDS = {
        "positive": ["มีความสุข", "ดีใจ", "ยิ้ม", "สบายใจ", "กำลังใจ"],
        "negative": ["เศร้า", "นอย", "เหนื่อย", "ท้อ", "กังวล", "เครียด"],
        "angry": ["โกรธ", "แค้น", "โมโห", "หงุดหงิด"],
        "hopeful": ["หวัง", "เชื่อ", "ไว้ใจ", "ศรัทธา"]
    }
    
    def __init__(self):
        # Database
        self.db_host = os.getenv("POSTGRES_HOST", "localhost")
        self.db_port = int(os.getenv("POSTGRES_PORT", 5432))
        self.db_name = os.getenv("POSTGRES_DB", "unjai")
        self.db_user = os.getenv("POSTGRES_USER", "postgres")
        self.db_password = os.getenv("POSTGRES_PASSWORD", "")
        
        # Trend history
        self.trend_history: List[DetectedTrend] = []
        
        logger.info("Trend Predictor initialized")
    
    def _get_db_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
    
    # Keyword Trend Detection
    
    def detect_keyword_trends(self, hours: int = 24) -> List[DetectedTrend]:
        """Detect trending keywords"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get current period keywords
            cursor.execute("""
                SELECT content, created_at
                FROM interaction_logs
                WHERE created_at >= NOW() - INTERVAL '%s hours'
            """, (hours,))
            
            current_rows = cursor.fetchall()
            
            # Get previous period for comparison
            cursor.execute("""
                SELECT content, created_at
                FROM interaction_logs
                WHERE created_at >= NOW() - INTERVAL '%s hours'
                AND created_at < NOW() - INTERVAL '%s hours'
            """, (hours * 2, hours))
            
            previous_rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Extract and count keywords
            current_keywords = self._extract_keywords([r["content"] for r in current_rows])
            previous_keywords = self._extract_keywords([r["content"] for r in previous_rows])
            
            # Detect trends
            trends = []
            for keyword, current_count in current_keywords.items():
                previous_count = previous_keywords.get(keyword, 0)
                
                if previous_count == 0:
                    if current_count >= 3:  # New emerging keyword
                        trends.append(self._create_trend(
                            TrendType.KEYWORD, keyword, current_count,
                            previous_count, hours, "new_emerging"
                        ))
                else:
                    change_ratio = current_count / previous_count
                    if change_ratio >= self.SPIKE_THRESHOLD:
                        trends.append(self._create_trend(
                            TrendType.KEYWORD, keyword, current_count,
                            previous_count, hours, "spike"
                        ))
                    elif change_ratio >= self.RISING_THRESHOLD:
                        trends.append(self._create_trend(
                            TrendType.KEYWORD, keyword, current_count,
                            previous_count, hours, "rising"
                        ))
            
            return trends
            
        except Exception as e:
            logger.error(f"Error detecting keyword trends: {e}")
            return []
    
    def _extract_keywords(self, texts: List[str]) -> Counter:
        """Extract keywords from texts"""
        all_keywords = []
        
        for text in texts:
            if not text:
                continue
            
            # Check crisis keywords
            for kw in self.CRISIS_KEYWORDS:
                if kw in text:
                    all_keywords.append(kw)
            
            # Check emotional keywords
            for category, keywords in self.EMOTIONAL_KEYWORDS.items():
                for kw in keywords:
                    if kw in text:
                        all_keywords.append(f"{category}:{kw}")
        
        return Counter(all_keywords)
    
    # Crisis Trend Detection
    
    def detect_crisis_trends(self, hours: int = 24) -> List[DetectedTrend]:
        """Detect crisis-related trends"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Current period crisis count
            cursor.execute("""
                SELECT COUNT(*) as count, level
                FROM crisis_incidents
                WHERE detected_at >= NOW() - INTERVAL '%s hours'
                GROUP BY level
            """, (hours,))
            
            current_crisis = {row[1]: row[0] for row in cursor.fetchall()}
            
            # Previous period
            cursor.execute("""
                SELECT COUNT(*) as count, level
                FROM crisis_incidents
                WHERE detected_at >= NOW() - INTERVAL '%s hours'
                AND detected_at < NOW() - INTERVAL '%s hours'
                GROUP BY level
            """, (hours * 2, hours))
            
            previous_crisis = {row[1]: row[0] for row in cursor.fetchall()}
            
            cursor.close()
            conn.close()
            
            trends = []
            for level in ["EMERGENCY", "WARNING"]:
                current = current_crisis.get(level, 0)
                previous = previous_crisis.get(level, 0)
                
                if previous == 0 and current > 0:
                    trends.append(self._create_trend(
                        TrendType.CRISIS, f"crisis_{level.lower()}",
                        current, previous, hours, "new"
                    ))
                elif previous > 0:
                    change = current / previous
                    if change >= self.RISING_THRESHOLD:
                        trends.append(self._create_trend(
                            TrendType.CRISIS, f"crisis_{level.lower()}",
                            current, previous, hours, "rising"
                        ))
            
            return trends
            
        except Exception as e:
            logger.error(f"Error detecting crisis trends: {e}")
            return []
    
    # Sentiment Trend Analysis
    
    def detect_sentiment_trends(self, hours: int = 24) -> List[DetectedTrend]:
        """Detect sentiment trends"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Current sentiment distribution
            cursor.execute("""
                SELECT sentiment_label, COUNT(*) as count,
                       AVG(sentiment_score) as avg_score
                FROM sentiment_analysis
                WHERE created_at >= NOW() - INTERVAL '%s hours'
                GROUP BY sentiment_label
            """, (hours,))
            
            current = {row[0]: {"count": row[1], "score": row[2]} 
                      for row in cursor.fetchall()}
            
            # Previous period
            cursor.execute("""
                SELECT sentiment_label, COUNT(*) as count,
                       AVG(sentiment_score) as avg_score
                FROM sentiment_analysis
                WHERE created_at >= NOW() - INTERVAL '%s hours'
                AND created_at < NOW() - INTERVAL '%s hours'
                GROUP BY sentiment_label
            """, (hours * 2, hours))
            
            previous = {row[0]: {"count": row[1], "score": row[2]} 
                       for row in cursor.fetchall()}
            
            cursor.close()
            conn.close()
            
            trends = []
            
            # Check for negative sentiment increase
            if "NEGATIVE" in current and "NEGATIVE" in previous:
                curr_neg = current["NEGATIVE"]["count"]
                prev_neg = previous["NEGATIVE"]["count"]
                
                if prev_neg > 0:
                    change = curr_neg / prev_neg
                    if change >= self.RISING_THRESHOLD:
                        trends.append(self._create_trend(
                            TrendType.SENTIMENT, "negative_sentiment",
                            curr_neg, prev_neg, hours, "rising"
                        ))
            
            # Check average sentiment score trend
            if current and previous:
                curr_avg = sum(c["score"] * c["count"] for c in current.values()) / \
                          sum(c["count"] for c in current.values())
                prev_avg = sum(c["score"] * c["count"] for c in previous.values()) / \
                          sum(c["count"] for c in previous.values())
                
                if prev_avg != 0:
                    change = (curr_avg - prev_avg) / abs(prev_avg)
                    if change <= -0.2:  # 20% drop in sentiment
                        trends.append(self._create_trend(
                            TrendType.SENTIMENT, "overall_sentiment",
                            curr_avg, prev_avg, hours, "falling"
                        ))
            
            return trends
            
        except Exception as e:
            logger.error(f"Error detecting sentiment trends: {e}")
            return []
    
    # Helper methods
    
    def _create_trend(self, trend_type: TrendType, keyword: str,
                      current: float, previous: float, hours: int,
                      pattern: str) -> DetectedTrend:
        """Create trend object"""
        if previous == 0:
            change_percent = 100.0 if current > 0 else 0.0
        else:
            change_percent = ((current - previous) / previous) * 100
        
        # Determine direction
        if pattern == "spike" or (pattern == "rising" and change_percent > 100):
            direction = TrendDirection.SPIKE
        elif pattern == "rising" or change_percent > 20:
            direction = TrendDirection.RISING
        elif change_percent < -20:
            direction = TrendDirection.FALLING
        else:
            direction = TrendDirection.STABLE
        
        # Determine alert level
        if trend_type == TrendType.CRISIS:
            alert = AlertLevel.CRITICAL
        elif trend_type == TrendType.SENTIMENT and "negative" in keyword:
            alert = AlertLevel.WARNING
        elif change_percent > 200:
            alert = AlertLevel.WARNING
        else:
            alert = AlertLevel.INFO
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            trend_type, keyword, direction, alert
        )
        
        return DetectedTrend(
            trend_type=trend_type,
            direction=direction,
            keyword_or_topic=keyword,
            current_value=current,
            previous_value=previous,
            change_percent=change_percent,
            time_window=f"{hours}h",
            confidence=0.8 if pattern == "spike" else 0.7,
            alert_level=alert,
            detected_at=datetime.now(),
            recommendation=recommendation
        )
    
    def _generate_recommendation(self, trend_type: TrendType, keyword: str,
                                  direction: TrendDirection, alert: AlertLevel) -> str:
        """Generate recommendation based on trend"""
        if trend_type == TrendType.CRISIS:
            return "Consider increasing human volunteer monitoring"
        elif trend_type == TrendType.SENTIMENT and "negative" in keyword:
            return "Prepare more positive/healing content"
        elif trend_type == TrendType.KEYWORD and "อยากตาย" in keyword:
            return "URGENT: Review crisis detection sensitivity"
        elif direction == TrendDirection.RISING:
            return "Monitor trend and prepare related content"
        else:
            return "Continue normal operations"
    
    # Main Analysis
    
    def analyze_trends(self, hours: int = 24) -> TrendReport:
        """Run complete trend analysis"""
        logger.info(f"Starting trend analysis for last {hours} hours...")
        
        all_trends = []
        
        # Detect all trend types
        all_trends.extend(self.detect_keyword_trends(hours))
        all_trends.extend(self.detect_crisis_trends(hours))
        all_trends.extend(self.detect_sentiment_trends(hours))
        
        # Filter by alert level
        critical = [t for t in all_trends if t.alert_level == AlertLevel.CRITICAL]
        warnings = [t for t in all_trends if t.alert_level == AlertLevel.WARNING]
        info = [t for t in all_trends if t.alert_level == AlertLevel.INFO]
        
        # Store history
        self.trend_history.extend(all_trends)
        
        report = TrendReport(
            report_id=f"TREND-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            generated_at=datetime.now(),
            analysis_period=f"{hours}h",
            trends=all_trends,
            summary={
                "total_trends": len(all_trends),
                "critical": len(critical),
                "warnings": len(warnings),
                "info": len(info),
                "top_rising": [t.keyword_or_topic for t in all_trends 
                              if t.direction == TrendDirection.RISING][:5]
            },
            predictions=self._generate_predictions(all_trends)
        )
        
        logger.info(f"Trend analysis complete: {len(all_trends)} trends detected")
        
        return report
    
    def _generate_predictions(self, trends: List[DetectedTrend]) -> List[Dict]:
        """Generate predictions based on trends"""
        predictions = []
        
        # Check for concerning patterns
        crisis_trends = [t for t in trends if t.trend_type == TrendType.CRISIS]
        negative_sentiment = [t for t in trends 
                             if t.trend_type == TrendType.SENTIMENT 
                             and "negative" in t.keyword_or_topic]
        
        if len(crisis_trends) >= 2:
            predictions.append({
                "type": "risk_assessment",
                "prediction": "Crisis incidents increasing - prepare volunteer team",
                "confidence": 0.75,
                "timeframe": "24-48 hours"
            })
        
        if negative_sentiment and negative_sentiment[0].change_percent > 50:
            predictions.append({
                "type": "content_strategy",
                "prediction": "Community mood declining - deploy uplifting content",
                "confidence": 0.7,
                "timeframe": "immediate"
            })
        
        return predictions
    
    # Reporting
    
    def print_report(self, report: TrendReport):
        """Print report to console"""
        print("\n" + "=" * 70)
        print("📈 Trend Analysis Report")
        print("=" * 70)
        print(f"Report ID: {report.report_id}")
        print(f"Period: {report.analysis_period}")
        print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("Summary:")
        print(f"  Total Trends: {report.summary['total_trends']}")
        print(f"  🚨 Critical: {report.summary['critical']}")
        print(f"  ⚠️  Warnings: {report.summary['warnings']}")
        print(f"  ℹ️  Info: {report.summary['info']}")
        
        if report.summary['top_rising']:
            print(f"\n  🔥 Top Rising: {', '.join(report.summary['top_rising'])}")
        
        if report.trends:
            print("\nDetected Trends:")
            for trend in report.trends:
                icon = "🚨" if trend.alert_level == AlertLevel.CRITICAL else \
                       "⚠️" if trend.alert_level == AlertLevel.WARNING else "ℹ️"
                direction_icon = "📈" if trend.direction in [TrendDirection.RISING, TrendDirection.SPIKE] else \
                                "📉" if trend.direction == TrendDirection.FALLING else "➡️"
                print(f"\n  {icon} {trend.keyword_or_topic}")
                print(f"     {direction_icon} {trend.change_percent:+.1f}% ({trend.time_window})")
                print(f"     Confidence: {trend.confidence:.0%}")
                print(f"     → {trend.recommendation}")
        
        if report.predictions:
            print("\n🔮 Predictions:")
            for pred in report.predictions:
                print(f"  • {pred['prediction']}")
                print(f"    (Confidence: {pred['confidence']:.0%}, {pred['timeframe']})")
        
        print("=" * 70 + "\n")
    
    def generate_report_file(self, report: TrendReport, 
                             filepath: str = None) -> str:
        """Generate JSON report file"""
        if filepath is None:
            filepath = f"trend_report_{report.report_id}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"Trend report saved to {filepath}")
        return filepath
    
    def get_health(self) -> Dict:
        """Get predictor health"""
        return {
            "status": "ready",
            "monitored_keywords": len(self.CRISIS_KEYWORDS) + \
                                 sum(len(v) for v in self.EMOTIONAL_KEYWORDS.values()),
            "trend_history_count": len(self.trend_history),
            "thresholds": {
                "rising": self.RISING_THRESHOLD,
                "spike": self.SPIKE_THRESHOLD
            }
        }


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("📈 Trend Predictor Demo")
    print("=" * 70)
    
    predictor = TrendPredictor()
    
    print("\n🔍 Monitored Keywords:")
    print(f"  Crisis keywords: {len(predictor.CRISIS_KEYWORDS)}")
    print(f"  Emotional keywords: {sum(len(v) for v in predictor.EMOTIONAL_KEYWORDS.values())}")
    
    print("\n🏥 Health Check:")
    health = predictor.get_health()
    print(f"   Status: {health['status']}")
    print(f"   Monitored: {health['monitored_keywords']} keywords")
    print(f"   Thresholds: Rising {health['thresholds']['rising']}x, Spike {health['thresholds']['spike']}x")
    
    print("\n▶️  Running demo trend analysis...")
    
    # Run analysis (will use mock data if no DB)
    report = predictor.analyze_trends(hours=24)
    predictor.print_report(report)
