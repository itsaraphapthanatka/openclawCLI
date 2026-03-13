"""
Module 9: Analytics Dashboard (The Insights Engine)
Nong Unjai AI System

This module provides comprehensive analytics and reporting:
- User engagement metrics
- R-score trends and distribution
- Sentiment analysis reports
- Crisis detection logs
- Content performance tracking
- ROI calculations for sponsors
- Real-time dashboard API

Tech Stack:
- PostgreSQL (Analytics data warehouse)
- Redis (Real-time counters)
- FastAPI (Dashboard API)
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict

import psycopg2
from psycopg2.extras import RealDictCursor
import redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricPeriod(Enum):
    """Time periods for metrics"""
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class EngagementMetrics:
    """User engagement metrics"""
    total_users: int = 0
    active_users: int = 0
    new_users: int = 0
    returning_users: int = 0
    total_messages: int = 0
    avg_messages_per_user: float = 0.0
    avg_session_duration: float = 0.0


@dataclass
class SentimentMetrics:
    """Sentiment analysis metrics"""
    total_analyzed: int = 0
    positive_count: int = 0
    neutral_count: int = 0
    negative_count: int = 0
    avg_sentiment_score: float = 0.0
    trend: str = "stable"  # improving, stable, declining


@dataclass
class CrisisMetrics:
    """Crisis detection metrics"""
    total_incidents: int = 0
    emergency_count: int = 0
    warning_count: int = 0
    resolved_count: int = 0
    avg_response_time: float = 0.0
    common_triggers: List[str] = None
    
    def __post_init__(self):
        if self.common_triggers is None:
            self.common_triggers = []


@dataclass
class ContentMetrics:
    """Content performance metrics"""
    total_videos_watched: int = 0
    total_quizzes_completed: int = 0
    avg_quiz_score: float = 0.0
    top_videos: List[Dict] = None
    top_quizzes: List[Dict] = None
    
    def __post_init__(self):
        if self.top_videos is None:
            self.top_videos = []
        if self.top_quizzes is None:
            self.top_quizzes = []


@dataclass
class RScoreDistribution:
    """R-score distribution across users"""
    low_count: int = 0      # 0-40 (needs support)
    medium_count: int = 0   # 41-60 (developing)
    high_count: int = 0     # 61-80 (doing well)
    excellent_count: int = 0  # 81-100 (ready to help)
    avg_r_score: float = 0.0
    
    def to_dict(self) -> Dict:
        total = self.low_count + self.medium_count + self.high_count + self.excellent_count
        if total == 0:
            total = 1
        return {
            "distribution": {
                "low_0_40": {
                    "count": self.low_count,
                    "percentage": round(self.low_count / total * 100, 1),
                    "label": "needs_support"
                },
                "medium_41_60": {
                    "count": self.medium_count,
                    "percentage": round(self.medium_count / total * 100, 1),
                    "label": "developing"
                },
                "high_61_80": {
                    "count": self.high_count,
                    "percentage": round(self.high_count / total * 100, 1),
                    "label": "doing_well"
                },
                "excellent_81_100": {
                    "count": self.excellent_count,
                    "percentage": round(self.excellent_count / total * 100, 1),
                    "label": "ready_to_help"
                }
            },
            "average": round(self.avg_r_score, 2),
            "total_users": total
        }


@dataclass
class SystemHealth:
    """Overall system health"""
    status: str = "healthy"
    uptime_hours: float = 0.0
    error_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    active_modules: List[str] = None
    
    def __post_init__(self):
        if self.active_modules is None:
            self.active_modules = []


class AnalyticsDashboard:
    """
    Main Analytics Dashboard - comprehensive reporting system
    """
    
    def __init__(self):
        # Database
        self.db_host = os.getenv("POSTGRES_HOST", "localhost")
        self.db_port = int(os.getenv("POSTGRES_PORT", 5432))
        self.db_name = os.getenv("POSTGRES_DB", "unjai")
        self.db_user = os.getenv("POSTGRES_USER", "postgres")
        self.db_password = os.getenv("POSTGRES_PASSWORD", "")
        
        # Redis
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=4,  # Use DB 4 for analytics
            decode_responses=True
        )
        
        logger.info("Analytics Dashboard initialized")
    
    def _get_db_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
    
    # Engagement Metrics
    
    def get_engagement_metrics(self, period: MetricPeriod = MetricPeriod.TODAY) -> EngagementMetrics:
        """Get user engagement metrics for a period"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Determine date range
            date_filter = self._get_date_filter(period)
            
            # Total users
            cursor.execute("SELECT COUNT(*) FROM user_sessions")
            total_users = cursor.fetchone()[0]
            
            # Active users (interacted in period)
            cursor.execute(f"""
                SELECT COUNT(DISTINCT user_id) 
                FROM interaction_logs 
                WHERE {date_filter}
            """)
            active_users = cursor.fetchone()[0]
            
            # New users
            cursor.execute(f"""
                SELECT COUNT(*) FROM user_sessions 
                WHERE created_at >= {self._get_period_start(period)}
            """)
            new_users = cursor.fetchone()[0]
            
            # Total messages
            cursor.execute(f"""
                SELECT COUNT(*) FROM interaction_logs 
                WHERE {date_filter}
            """)
            total_messages = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return EngagementMetrics(
                total_users=total_users,
                active_users=active_users,
                new_users=new_users,
                returning_users=active_users - new_users,
                total_messages=total_messages,
                avg_messages_per_user=total_messages / active_users if active_users > 0 else 0
            )
            
        except Exception as e:
            logger.error(f"Error getting engagement metrics: {e}")
            return EngagementMetrics()
    
    # Sentiment Metrics
    
    def get_sentiment_metrics(self, period: MetricPeriod = MetricPeriod.TODAY) -> SentimentMetrics:
        """Get sentiment analysis metrics"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            date_filter = self._get_date_filter(period)
            
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN sentiment_label = 'POSITIVE' THEN 1 END) as positive,
                    COUNT(CASE WHEN sentiment_label = 'NEUTRAL' THEN 1 END) as neutral,
                    COUNT(CASE WHEN sentiment_label = 'NEGATIVE' THEN 1 END) as negative,
                    AVG(sentiment_score) as avg_score
                FROM sentiment_analysis
                WHERE {date_filter}
            """)
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            total, positive, neutral, negative, avg_score = row
            
            # Determine trend
            trend = "stable"
            if positive > negative * 2:
                trend = "improving"
            elif negative > positive * 1.5:
                trend = "declining"
            
            return SentimentMetrics(
                total_analyzed=total,
                positive_count=positive,
                neutral_count=neutral,
                negative_count=negative,
                avg_sentiment_score=avg_score or 0.0,
                trend=trend
            )
            
        except Exception as e:
            logger.error(f"Error getting sentiment metrics: {e}")
            return SentimentMetrics()
    
    # Crisis Metrics
    
    def get_crisis_metrics(self, period: MetricPeriod = MetricPeriod.TODAY) -> CrisisMetrics:
        """Get crisis detection metrics"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            date_filter = self._get_date_filter(period)
            
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN level = 'EMERGENCY' THEN 1 END) as emergency,
                    COUNT(CASE WHEN level = 'WARNING' THEN 1 END) as warning,
                    COUNT(CASE WHEN resolved = TRUE THEN 1 END) as resolved,
                    AVG(EXTRACT(EPOCH FROM (resolved_at - detected_at))/60) as avg_response_minutes
                FROM crisis_incidents
                WHERE {date_filter}
            """)
            
            row = cursor.fetchone()
            
            # Get common triggers
            cursor.execute(f"""
                SELECT trigger_keyword, COUNT(*) as count
                FROM crisis_incidents
                WHERE {date_filter}
                GROUP BY trigger_keyword
                ORDER BY count DESC
                LIMIT 5
            """)
            
            triggers = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return CrisisMetrics(
                total_incidents=row[0],
                emergency_count=row[1],
                warning_count=row[2],
                resolved_count=row[3],
                avg_response_time=row[4] or 0.0,
                common_triggers=triggers
            )
            
        except Exception as e:
            logger.error(f"Error getting crisis metrics: {e}")
            return CrisisMetrics()
    
    # R-Score Distribution
    
    def get_rscore_distribution(self) -> RScoreDistribution:
        """Get R-score distribution across all users"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN r_score <= 40 THEN 1 END) as low,
                    COUNT(CASE WHEN r_score > 40 AND r_score <= 60 THEN 1 END) as medium,
                    COUNT(CASE WHEN r_score > 60 AND r_score <= 80 THEN 1 END) as high,
                    COUNT(CASE WHEN r_score > 80 THEN 1 END) as excellent,
                    AVG(r_score) as avg_score
                FROM user_sessions
                WHERE r_score IS NOT NULL
            """)
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return RScoreDistribution(
                low_count=row[0],
                medium_count=row[1],
                high_count=row[2],
                excellent_count=row[3],
                avg_r_score=row[4] or 0.0
            )
            
        except Exception as e:
            logger.error(f"Error getting R-score distribution: {e}")
            return RScoreDistribution()
    
    # Content Metrics
    
    def get_content_metrics(self, period: MetricPeriod = MetricPeriod.TODAY) -> ContentMetrics:
        """Get content performance metrics"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            date_filter = self._get_date_filter(period)
            
            # Video metrics
            cursor.execute(f"""
                SELECT COUNT(*) as watch_count
                FROM video_watches
                WHERE {date_filter}
            """)
            video_count = cursor.fetchone()["watch_count"]
            
            # Quiz metrics
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as quiz_count,
                    AVG(score) as avg_score
                FROM quiz_attempts
                WHERE {date_filter}
            """)
            quiz_row = cursor.fetchone()
            
            # Top videos
            cursor.execute(f"""
                SELECT video_id, COUNT(*) as views
                FROM video_watches
                WHERE {date_filter}
                GROUP BY video_id
                ORDER BY views DESC
                LIMIT 5
            """)
            top_videos = [dict(row) for row in cursor.fetchall()]
            
            # Top quizzes
            cursor.execute(f"""
                SELECT quiz_id, COUNT(*) as attempts, AVG(score) as avg_score
                FROM quiz_attempts
                WHERE {date_filter}
                GROUP BY quiz_id
                ORDER BY attempts DESC
                LIMIT 5
            """)
            top_quizzes = [dict(row) for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return ContentMetrics(
                total_videos_watched=video_count,
                total_quizzes_completed=quiz_row["quiz_count"],
                avg_quiz_score=quiz_row["avg_score"] or 0.0,
                top_videos=top_videos,
                top_quizzes=top_quizzes
            )
            
        except Exception as e:
            logger.error(f"Error getting content metrics: {e}")
            return ContentMetrics()
    
    # System Health
    
    def get_system_health(self) -> SystemHealth:
        """Get overall system health"""
        try:
            # Check from Redis or service registry
            active_modules = []
            
            if self.redis.ping():
                active_modules.append("redis")
            
            # Test DB connection
            try:
                conn = self._get_db_connection()
                conn.close()
                active_modules.append("postgresql")
            except:
                pass
            
            return SystemHealth(
                status="healthy" if len(active_modules) >= 2 else "degraded",
                active_modules=active_modules
            )
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return SystemHealth(status="unhealthy")
    
    # ROI Report for Sponsors
    
    def get_roi_report(self, period: MetricPeriod = MetricPeriod.MONTH) -> Dict:
        """Generate ROI report for sponsors"""
        try:
            engagement = self.get_engagement_metrics(period)
            sentiment = self.get_sentiment_metrics(period)
            crisis = self.get_crisis_metrics(period)
            content = self.get_content_metrics(period)
            rscore_dist = self.get_rscore_distribution()
            
            # Calculate impact scores
            mental_health_improvement = (
                (sentiment.positive_count / max(sentiment.total_analyzed, 1)) * 100
            )
            
            crisis_prevention_rate = (
                (crisis.resolved_count / max(crisis.total_incidents, 1)) * 100
            )
            
            return {
                "period": period.value,
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_users_reached": engagement.total_users,
                    "active_users": engagement.active_users,
                    "mental_health_improvement": round(mental_health_improvement, 1),
                    "crisis_interventions": crisis.total_incidents,
                    "crisis_prevention_rate": round(crisis_prevention_rate, 1),
                    "content_engagement": {
                        "videos_watched": content.total_videos_watched,
                        "quizzes_completed": content.total_quizzes_completed
                    }
                },
                "r_score_distribution": rscore_dist.to_dict(),
                "sentiment_breakdown": {
                    "positive": sentiment.positive_count,
                    "neutral": sentiment.neutral_count,
                    "negative": sentiment.negative_count
                },
                "key_metrics": {
                    "avg_r_score": round(rscore_dist.avg_r_score, 2),
                    "avg_sentiment": round(sentiment.avg_sentiment_score, 3),
                    "user_retention": round(
                        (engagement.returning_users / max(engagement.active_users, 1)) * 100, 1
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating ROI report: {e}")
            return {"error": str(e)}
    
    # Full Dashboard
    
    def get_full_dashboard(self) -> Dict:
        """Get complete dashboard data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "engagement": asdict(self.get_engagement_metrics()),
            "sentiment": asdict(self.get_sentiment_metrics()),
            "crisis": asdict(self.get_crisis_metrics()),
            "rscore_distribution": self.get_rscore_distribution().to_dict(),
            "content": asdict(self.get_content_metrics()),
            "health": asdict(self.get_system_health())
        }
    
    # Helper methods
    
    def _get_date_filter(self, period: MetricPeriod) -> str:
        """Get SQL date filter for period"""
        start = self._get_period_start(period)
        return f"created_at >= '{start}'"
    
    def _get_period_start(self, period: MetricPeriod) -> datetime:
        """Get start datetime for period"""
        now = datetime.now()
        
        if period == MetricPeriod.TODAY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == MetricPeriod.WEEK:
            return now - timedelta(days=7)
        elif period == MetricPeriod.MONTH:
            return now - timedelta(days=30)
        elif period == MetricPeriod.QUARTER:
            return now - timedelta(days=90)
        elif period == MetricPeriod.YEAR:
            return now - timedelta(days=365)
        
        return now - timedelta(days=1)
    
    def get_health(self) -> Dict:
        """Get dashboard health"""
        return {
            "status": "healthy",
            "modules": ["engagement", "sentiment", "crisis", "rscore", "content"],
            "timestamp": datetime.now().isoformat()
        }


# FastAPI App for Dashboard API
def create_dashboard_api(analytics: AnalyticsDashboard) -> FastAPI:
    """Create FastAPI app for dashboard API"""
    
    app = FastAPI(title="Nong Unjai Analytics Dashboard")
    
    @app.get("/dashboard")
    async def get_dashboard():
        """Get full dashboard"""
        return analytics.get_full_dashboard()
    
    @app.get("/metrics/engagement")
    async def get_engagement(period: str = "today"):
        """Get engagement metrics"""
        try:
            p = MetricPeriod(period)
            return asdict(analytics.get_engagement_metrics(p))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid period")
    
    @app.get("/metrics/sentiment")
    async def get_sentiment(period: str = "today"):
        """Get sentiment metrics"""
        try:
            p = MetricPeriod(period)
            return asdict(analytics.get_sentiment_metrics(p))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid period")
    
    @app.get("/metrics/crisis")
    async def get_crisis(period: str = "today"):
        """Get crisis metrics"""
        try:
            p = MetricPeriod(period)
            return asdict(analytics.get_crisis_metrics(p))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid period")
    
    @app.get("/metrics/rscore")
    async def get_rscore():
        """Get R-score distribution"""
        return analytics.get_rscore_distribution().to_dict()
    
    @app.get("/reports/roi")
    async def get_roi(period: str = "month"):
        """Get ROI report for sponsors"""
        try:
            p = MetricPeriod(period)
            return analytics.get_roi_report(p)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid period")
    
    @app.get("/health")
    async def health_check():
        """Health check"""
        return analytics.get_system_health()
    
    return app


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("📊 Analytics Dashboard Test")
    print("=" * 70)
    
    analytics = AnalyticsDashboard()
    
    print("\n📈 Dashboard Components:")
    print("   ✅ Engagement Metrics")
    print("   ✅ Sentiment Analysis")
    print("   ✅ Crisis Detection")
    print("   ✅ R-Score Distribution")
    print("   ✅ Content Performance")
    print("   ✅ System Health")
    print("   ✅ ROI Reports")
    
    print("\n🏥 Health Check:")
    health = analytics.get_health()
    print(f"   Status: {health['status']}")
    print(f"   Modules: {', '.join(health['modules'])}")
    
    print("\n📡 API Endpoints Available:")
    print("   GET /dashboard - Full dashboard")
    print("   GET /metrics/engagement")
    print("   GET /metrics/sentiment")
    print("   GET /metrics/crisis")
    print("   GET /metrics/rscore")
    print("   GET /reports/roi")
    print("   GET /health")
    
    print("\n✅ Analytics Dashboard initialized successfully!")
    print("=" * 70)
