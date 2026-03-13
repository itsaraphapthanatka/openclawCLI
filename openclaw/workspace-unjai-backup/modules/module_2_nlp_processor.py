"""
Module 2: NLP Processor (The Mind Reader)
Nong Unjai AI System

This module handles:
- Sentiment Analysis (Thai + English) with intensity scoring
- Intent Classification (greeting, venting, crisis, bible_question, etc.)
- R-score (Ready Heart Score) calculation
- SOSVE (Suicide/self-harm) detection and alerting
- Entity extraction (emotions, topics, urgency)
- Persona recommendation based on user state

Tech Stack:
- Transformers (Hugging Face) for sentiment
- scikit-learn/Regex for intent classification
- Thai NLP (PyThaiNLP) for Thai text processing
- Custom models for domain-specific tasks
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging

import numpy as np
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    pipeline,
    Pipeline
)
import torch
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentLabel(Enum):
    """Sentiment classification labels"""
    VERY_NEGATIVE = -1.0   # < -0.7
    NEGATIVE = -0.5        # -0.7 to -0.3
    SLIGHTLY_NEGATIVE = -0.2  # -0.3 to -0.1
    NEUTRAL = 0.0          # -0.1 to 0.1
    SLIGHTLY_POSITIVE = 0.2   # 0.1 to 0.3
    POSITIVE = 0.5         # 0.3 to 0.7
    VERY_POSITIVE = 1.0    # > 0.7


class IntentType(Enum):
    """Intent classification types"""
    GREETING = "greeting"           # ทักทาย
    SMALL_TALK = "small_talk"       # คุยเล่น
    EMOTIONAL_SUPPORT = "emotional_support"  # ต้องการเยียวยา
    BIBLE_QUESTION = "bible_question"        # ถามพระคัมภีร์
    THEOLOGY_QUESTION = "theology_question"  # ถามปรัชญาศาสนา
    CRISIS = "crisis"               # วิกฤต (SOSVE)
    REQUEST_VIDEO = "request_video" # ขอคลิปหนุนใจ
    QUIZ_ANSWER = "quiz_answer"     # ตอบควิซ
    GRATITUDE = "gratitude"         # ขอบคุณ
    COMPLAINT = "complaint"         # บ่น/ระบาย
    GOODBYE = "goodbye"             # ลาก่อน
    UNKNOWN = "unknown"             # ไม่แน่ใจ


class CrisisLevel(Enum):
    """Crisis severity levels"""
    NONE = 0           # ไม่มีวิกฤต
    WARNING = 1        # สัญญาณเตือน (Warning Mode)
    EMERGENCY = 2      # วิกฤต (SOSVE Mode)


@dataclass
class SentimentResult:
    """Sentiment analysis result"""
    score: float                    # -1.0 to 1.0
    label: SentimentLabel
    confidence: float               # 0.0 to 1.0
    emotions: List[str]             # detected emotions: ["sad", "angry", "anxious"]
    explanation: str                # human-readable explanation


@dataclass
class IntentResult:
    """Intent classification result"""
    primary_intent: IntentType
    confidence: float
    secondary_intents: List[Tuple[IntentType, float]]  # [(intent, confidence), ...]
    entities: Dict[str, Any]        # extracted entities


@dataclass
class RScoreComponents:
    """Components for R-score calculation"""
    sentiment_score: float          # S (0-100)
    quiz_performance: float         # Q (0-100)
    interaction_frequency: float    # I (0-100)
    
    def calculate(self) -> float:
        """Calculate R-score: R = (S×0.4) + (Q×0.3) + (I×0.3)"""
        return (self.sentiment_score * 0.4) + \
               (self.quiz_performance * 0.3) + \
               (self.interaction_frequency * 0.3)


@dataclass
class CrisisDetectionResult:
    """Crisis detection result"""
    is_crisis: bool
    level: CrisisLevel
    trigger_keywords: List[str]
    recommended_action: str
    should_alert_human: bool


@dataclass
class NLPAnalysisResult:
    """Complete NLP analysis result"""
    original_text: str
    cleaned_text: str
    sentiment: SentimentResult
    intent: IntentResult
    r_score: float
    crisis: CrisisDetectionResult
    recommended_persona: int        # 1-12
    recommended_circle: int         # 1-3
    processing_time_ms: int
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "original_text": self.original_text,
            "cleaned_text": self.cleaned_text,
            "sentiment": {
                "score": self.sentiment.score,
                "label": self.sentiment.label.name,
                "confidence": self.sentiment.confidence,
                "emotions": self.sentiment.emotions,
                "explanation": self.sentiment.explanation
            },
            "intent": {
                "primary": self.intent.primary_intent.value,
                "confidence": self.intent.confidence,
                "secondary": [(i.value, c) for i, c in self.intent.secondary_intents],
                "entities": self.intent.entities
            },
            "r_score": self.r_score,
            "crisis": {
                "is_crisis": self.crisis.is_crisis,
                "level": self.crisis.level.name,
                "trigger_keywords": self.crisis.trigger_keywords,
                "should_alert": self.crisis.should_alert_human
            },
            "recommended_persona": self.recommended_persona,
            "recommended_circle": self.recommended_circle,
            "processing_time_ms": self.processing_time_ms
        }


class ThaiTextProcessor:
    """
    Thai language text processing utilities
    """
    
    def __init__(self):
        self.try_pythainlp = False
        try:
            from pythainlp import word_tokenize
            from pythainlp.corpus import thai_stopwords
            self.word_tokenize = word_tokenize
            self.thai_stopwords = thai_stopwords()
            self.try_pythainlp = True
            logger.info("PyThaiNLP loaded successfully")
        except ImportError:
            logger.warning("PyThaiNLP not installed, using fallback tokenizer")
            self.word_tokenize = None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize Thai text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Normalize repeated characters (e.g., "นอยยย" → "นอย")
        text = re.sub(r'(.)\1{2,}', r'\1\1', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove @mentions but keep names
        text = re.sub(r'@\w+', '', text)
        
        # Normalize common Thai chat abbreviations
        replacements = {
            "ค่ะ": "คะ",
            "ครับ": "คับ",
            "นอย": "เศร้า",
            "ยม": "เศร้า",
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize Thai text"""
        if self.try_pythainlp and self.word_tokenize:
            return self.word_tokenize(text, engine='newmm')
        else:
            # Fallback: simple character-based
            return list(text)
    
    def extract_emotion_words(self, text: str) -> List[str]:
        """Extract emotion-related words from Thai text"""
        emotion_keywords = {
            "sad": ["เศร้า", "นอย", "ยม", "หดหู่", "เสียใจ", "ร้องไห้", "ท้อ", "สิ้นหวัง", "เหงา"],
            "angry": ["โกรธ", "โมโห", "หงุดหงิด", "รำคาญ", "แค้น", "เกลียด", "บ่น"],
            "anxious": ["กังวล", "วิตก", "ตื่นเต้น", "กลัว", "หวาด", "เครียด", "กดดัน"],
            "happy": ["สุข", "ดีใจ", "มีความสุข", "สนุก", "รื่นเริง", "ยิ้ม", "หัวเราะ"],
            "tired": ["เหนื่อย", "ล้า", "หมดแรง", "อ่อนเพลีย", "ง่วง", "หิว"],
            "confused": ["สับสน", "งง", "ไม่เข้าใจ", "หลงทาง", "ลังเล"]
        }
        
        detected_emotions = []
        text_lower = text.lower()
        
        for emotion, keywords in emotion_keywords.items():
            if any(kw in text_lower for kw in keywords):
                detected_emotions.append(emotion)
        
        return detected_emotions


class CrisisDetector:
    """
    Detect crisis/suicide risk from text
    Based on HEARTBEAT.md SOSVE protocol
    """
    
    # Critical keywords - trigger immediate SOSVE (Persona 8)
    CRITICAL_KEYWORDS = [
        "อยากตาย", "ไม่อยากอยู่แล้ว", "ลาก่อน", "จบปัญหา", 
        "หลับไม่ตื่น", "ฆ่าตัวตาย", "ทำร้ายตัวเอง",
        "ไม่อยากตื่น", "อยากหายไป", "จบชีวิต", "ไปอยู่กับพระเจ้า",
        "ไม่ไหวแล้ว", "มืดแปดด้าน", "ไม่มีทางออก", 
        "โลกนี้ไม่มีที่สำหรับฉัน", "ทรมานเหลือเกิน", "ไม่เหลืออะไรแล้ว",
        "ไร้ค่า", "ไม่มีความหมาย", "อยากหายไปจากโลกนี้",
        "ขอโทษทุกคน", "ดูแลตัวเองด้วยนะ", "ลาก่อนทุกคน",
    ]
    
    # Warning keywords - require monitoring (Warning Mode)
    WARNING_KEYWORDS = [
        "พระเจ้าทอดทิ้ง", "ทำไมต้องเจอแบบนี้", "โกรธพระเจ้า",
        "เหนื่อยจัง", "ท้อใจ", "หมดหวัง", "เบื่อชีวิต",
        "อยากหนี", "อยากหายไป", "ไม่มีใครเข้าใจ",
        "นอนไม่หลับ", "ไม่มีความอยากอาหาร", "หายใจไม่ทัน"
    ]
    
    def detect(self, text: str, sentiment_score: float) -> CrisisDetectionResult:
        """Detect crisis level from text"""
        text_lower = text.lower()
        found_critical = []
        found_warning = []
        
        for keyword in self.CRITICAL_KEYWORDS:
            if keyword in text_lower:
                found_critical.append(keyword)
        
        for keyword in self.WARNING_KEYWORDS:
            if keyword in text_lower:
                found_warning.append(keyword)
        
        if found_critical or sentiment_score <= -0.9:
            return CrisisDetectionResult(
                is_crisis=True,
                level=CrisisLevel.EMERGENCY,
                trigger_keywords=found_critical,
                recommended_action="IMMEDIATE_SOSVE_PROTOCOL",
                should_alert_human=True
            )
        elif found_warning or sentiment_score <= -0.7:
            return CrisisDetectionResult(
                is_crisis=True,
                level=CrisisLevel.WARNING,
                trigger_keywords=found_warning,
                recommended_action="EMPATHETIC_LISTENING_PERSONA_2",
                should_alert_human=False
            )
        else:
            return CrisisDetectionResult(
                is_crisis=False,
                level=CrisisLevel.NONE,
                trigger_keywords=[],
                recommended_action="NORMAL_CONVERSATION",
                should_alert_human=False
            )


class IntentClassifier:
    """Classify user intent from text"""
    
    INTENT_PATTERNS = {
        IntentType.GREETING: [
            r'^(สวัสดี|หวัดดี|ดีค่ะ|ดีครับ|hi|hello|hey|สุ)',
        ],
        IntentType.GOODBYE: [
            r'(บาย|bye|ลาก่อน|ไปก่อน|พรุ่งนี้ค่อยคุย)',
        ],
        IntentType.GRATITUDE: [
            r'(ขอบคุณ|thx|thanks|thank you|ขอบใจ|เก่งมาก|ดีมาก)',
        ],
        IntentType.BIBLE_QUESTION: [
            r'(พระคัมภีร์|ข้อพระคัมภีร์|คัมภีร์|bible|scripture|ไบเบิล)',
            r'(ยอห์น|โรม|สดุดี|มัทธิว|มาระโก|ลูกา|กิจการ|วิวรณ์)',
        ],
        IntentType.THEOLOGY_QUESTION: [
            r'(ทำไมพระเจ้า|ทำไมพระเยซู|ทำไมต้อง|ปรัชญา|ศาสนา)',
            r'(พระเจ้ามีจริง|ความเชื่อ|ศรัทธา)',
        ],
        IntentType.REQUEST_VIDEO: [
            r'(ขอคลิป|อยากดูคลิป|มีคลิป|ส่งคลิป|clip|video|วิดีโอ)',
        ],
        IntentType.QUIZ_ANSWER: [
            r'(ตอบ|คำตอบ|เลือก|ข้อ \d|A|B|C|D|ควิซ|quiz)',
        ],
        IntentType.CRISIS: [
            r'(อยากตาย|ไม่อยากอยู่|ฆ่าตัว|สิ้นหวัง|ไม่ไหว)',
        ],
        IntentType.COMPLAINT: [
            r'(เหนื่อย|เบื่อ|งุ่นง่าย|โมโห|โกรธ|แย่|ห่วย)',
        ],
    }
    
    def classify(self, text: str, thai_processor: ThaiTextProcessor) -> IntentResult:
        """Classify intent from text"""
        text_lower = text.lower()
        scores = {}
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0.0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 0.5
            scores[intent] = min(score, 1.0)
        
        # Heuristics
        emotions = thai_processor.extract_emotion_words(text)
        if emotions and scores.get(IntentType.GREETING, 0) < 0.5:
            scores[IntentType.EMOTIONAL_SUPPORT] = scores.get(IntentType.EMOTIONAL_SUPPORT, 0) + 0.3
        
        if '?' in text or 'เหรอ' in text or 'ไหม' in text:
            if any(kw in text_lower for kw in ['พระเจ้า', 'พระเยซู', 'คัมภีร์']):
                scores[IntentType.BIBLE_QUESTION] = scores.get(IntentType.BIBLE_QUESTION, 0) + 0.3
        
        if len(text) < 20 and scores.get(IntentType.GREETING, 0) > 0:
            scores[IntentType.SMALL_TALK] = 0.8
        
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_intent = sorted_intents[0][0] if sorted_intents else IntentType.UNKNOWN
        primary_score = sorted_intents[0][1] if sorted_intents else 0.0
        
        entities = self._extract_entities(text, thai_processor)
        
        return IntentResult(
            primary_intent=primary_intent,
            confidence=primary_score,
            secondary_intents=sorted_intents[1:3],
            entities=entities
        )
    
    def _extract_entities(self, text: str, thai_processor: ThaiTextProcessor) -> Dict[str, Any]:
        """Extract relevant entities from text"""
        entities = {
            "emotions": thai_processor.extract_emotion_words(text),
            "has_question_mark": '?' in text,
            "message_length": len(text),
            "word_count": len(thai_processor.tokenize(text)),
            "topics": []
        }
        
        topic_keywords = {
            "work": ["งาน", "ออฟฟิศ", "เจ้านาย", "ลูกน้อง", "เงินเดือน"],
            "family": ["แม่", "พ่อ", "พี่", "น้อง", "ครอบครัว", "ลูก"],
            "relationship": ["แฟน", "แฟนเก่า", "คบ", "เลิก", "หย่า", "ความรัก"],
            "health": ["ป่วย", "เจ็บ", "โรงพยาบาล", "หมอ", "ยา"],
            "faith": ["พระเจ้า", "พระเยซู", "คริสตจักร", "อธิษฐาน", "พระคัมภีร์"],
        }
        
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                entities["topics"].append(topic)
        
        return entities


class SentimentAnalyzer:
    """Analyze sentiment from text using transformer model"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or "airesearch/wangchanberta-base-att-spm-uncased"
        self.pipeline = None
        self.thai_processor = ThaiTextProcessor()
        
        try:
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info(f"Sentiment model loaded: {self.model_name}")
        except Exception as e:
            logger.warning(f"Could not load transformer model: {e}")
            self.pipeline = None
    
    def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment of text"""
        cleaned = self.thai_processor.clean_text(text)
        
        if self.pipeline:
            try:
                result = self.pipeline(cleaned[:512])[0]
                label = result['label']
                confidence = result['score']
                
                if label == 'positive':
                    score = 0.5 + (confidence * 0.5)
                elif label == 'negative':
                    score = -0.5 - (confidence * 0.5)
                else:
                    score = (confidence - 0.5) * 0.2
                    
            except Exception as e:
                logger.error(f"Model inference error: {e}")
                score = self._rule_based_sentiment(cleaned)
                confidence = 0.5
        else:
            score = self._rule_based_sentiment(cleaned)
            confidence = 0.6
        
        emotions = self.thai_processor.extract_emotion_words(cleaned)
        
        if 'sad' in emotions or 'angry' in emotions:
            score = min(score, -0.3)
        elif 'happy' in emotions:
            score = max(score, 0.3)
        
        label = self._score_to_label(score)
        explanation = self._generate_explanation(score, emotions, label)
        
        return SentimentResult(
            score=score,
            label=label,
            confidence=confidence,
            emotions=emotions,
            explanation=explanation
        )
    
    def _rule_based_sentiment(self, text: str) -> float:
        """Fallback rule-based sentiment analysis"""
        positive_words = ["ดี", "สุข", "รัก", "ชอบ", "สนุก", "มีความสุข", "ยิ้ม", "หัวเราะ"]
        negative_words = ["แย่", "เศร้า", "โกรธ", "เกลียด", "กลัว", "กังวล", "เหนื่อย", "ท้อ"]
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        return (pos_count - neg_count) / total
    
    def _score_to_label(self, score: float) -> SentimentLabel:
        """Convert score to label"""
        if score < -0.7:
            return SentimentLabel.VERY_NEGATIVE
        elif score < -0.3:
            return SentimentLabel.NEGATIVE
        elif score < -0.1:
            return SentimentLabel.SLIGHTLY_NEGATIVE
        elif score < 0.1:
            return SentimentLabel.NEUTRAL
        elif score < 0.3:
            return SentimentLabel.SLIGHTLY_POSITIVE
        elif score < 0.7:
            return SentimentLabel.POSITIVE
        else:
            return SentimentLabel.VERY_POSITIVE
    
    def _generate_explanation(self, score: float, emotions: List[str], label: SentimentLabel) -> str:
        """Generate human-readable explanation"""
        if emotions:
            emotion_str = ", ".join(emotions)
            return f"Detected emotions: {emotion_str}. Overall sentiment: {label.name}"
        return f"Overall sentiment: {label.name} (score: {score:.2f})"


class PersonaRecommender:
    """Recommend persona based on analysis results"""
    
    # Persona mapping from IDENTITY.md
    PERSONA_MAP = {
        1: "พี่สาวสายปัญญา (Intellectual Truth Seeker)",
        2: "เพื่อนสาวสายเยียวยา (The Wounded Believer)",
        3: "น้องสาวสายกิจกรรม (Community-Driven Socialite)",
        4: "ที่ปรึกษาสายเป๊ะ (Value-Driven Professional)",
        5: "เพื่อนสนิทสายอธิษฐาน (The Caring Interceder)",
        6: "น้องอุ่นใจสายห่วงใย (The Passive Watcher)",
        7: "เพื่อนสาวจอมสงสัย (The Skeptical Challenger)",
        8: "หน่วยกู้ใจสายด่วน (The SOS / Acute Sufferer)",
        9: "ตัวตึงสายพระพร (The Authentic Vibe-Seeker / Gen Z)",
        10: "พี่สาวสายพักสงบ (The Exhausted Servant)",
        11: "น้องน้อยสายเก็บแต้ม (The Gamified Achiever)",
        12: "เพื่อนบ้านแสนดี (The Life-Transitioner)",
    }
    
    def recommend(self, 
                  sentiment: SentimentResult,
                  intent: IntentResult,
                  crisis: CrisisDetectionResult) -> Tuple[int, int]:
        """
        Recommend persona and circle level
        
        Returns:
            (persona_id, circle_level)
        """
        # Crisis override - always Persona 8
        if crisis.level == CrisisLevel.EMERGENCY:
            return (8, 1)  # Persona 8, Circle 1 (emergency)
        
        if crisis.level == CrisisLevel.WARNING:
            return (2, 1)  # Persona 2 (Healing), Circle 1
        
        # Intent-based recommendation
        intent_map = {
            IntentType.CRISIS: (8, 1),
            IntentType.BIBLE_QUESTION: (1, 2),
            IntentType.THEOLOGY_QUESTION: (7, 2),
            IntentType.EMOTIONAL_SUPPORT: (2, 1),
            IntentType.GREETING: (6, 1),
            IntentType.SMALL_TALK: (6, 1),
            IntentType.REQUEST_VIDEO: (3, 2),
            IntentType.QUIZ_ANSWER: (11, 2),
            IntentType.COMPLAINT: (2, 1),
            IntentType.GRATITUDE: (6, 1),
        }
        
        if intent.primary_intent in intent_map:
            return intent_map[intent.primary_intent]
        
        # Sentiment-based fallback
        if sentiment.score < -0.3:
            return (2, 1)  # Healing persona
        elif sentiment.score > 0.3:
            return (3, 2)  # Energetic persona
        
        # Default
        return (6, 1)


class NLPProcessor:
    """
    Main NLP Processor - combines all components
    Agent: NLP Processor (Agent #17)
    """
    
    def __init__(self, 
                 sentiment_model: Optional[str] = None,
                 enable_gpu: bool = False):
        """
        Initialize NLP Processor
        
        Args:
            sentiment_model: HuggingFace model name for sentiment
            enable_gpu: Whether to use GPU for inference
        """
        logger.info("Initializing NLP Processor...")
        
        self.thai_processor = ThaiTextProcessor()
        self.sentiment_analyzer = SentimentAnalyzer(sentiment_model)
        self.intent_classifier = IntentClassifier()
        self.crisis_detector = CrisisDetector()
        self.persona_recommender = PersonaRecommender()
        
        logger.info("NLP Processor initialized successfully")
    
    def analyze(self, text: str, 
                user_history: Optional[Dict] = None) -> NLPAnalysisResult:
        """
        Analyze text and return complete NLP result
        
        Args:
            text: User input text
            user_history: Optional user history for context
            
        Returns:
            NLPAnalysisResult
        """
        import time
        start_time = time.time()
        
        # Clean text
        cleaned_text = self.thai_processor.clean_text(text)
        
        # Sentiment analysis
        sentiment = self.sentiment_analyzer.analyze(text)
        
        # Intent classification
        intent = self.intent_classifier.classify(text, self.thai_processor)
        
        # Crisis detection
        crisis = self.crisis_detector.detect(text, sentiment.score)
        
        # R-score calculation (simplified - full version uses user history)
        r_components = RScoreComponents(
            sentiment_score=max(0, (sentiment.score + 1) * 50),  # Convert -1,1 to 0,100
            quiz_performance=50,  # Default - updated from quiz results
            interaction_frequency=50  # Default - updated from user activity
        )
        r_score = r_components.calculate()
        
        # Persona recommendation
        persona_id, circle_level = self.persona_recommender.recommend(
            sentiment, intent, crisis
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return NLPAnalysisResult(
            original_text=text,
            cleaned_text=cleaned_text,
            sentiment=sentiment,
            intent=intent,
            r_score=r_score,
            crisis=crisis,
            recommended_persona=persona_id,
            recommended_circle=circle_level,
            processing_time_ms=processing_time,
            timestamp=datetime.now()
        )
    
    def batch_analyze(self, texts: List[str]) -> List[NLPAnalysisResult]:
        """Analyze multiple texts"""
        return [self.analyze(text) for text in texts]
    
    def get_health(self) -> Dict:
        """Get system health status"""
        return {
            "status": "healthy",
            "components": {
                "thai_processor": "active",
                "sentiment_analyzer": "active" if self.sentiment_analyzer.pipeline else "fallback",
                "intent_classifier": "active",
                "crisis_detector": "active",
            },
            "model": self.sentiment_analyzer.model_name,
            "gpu_available": torch.cuda.is_available()
        }


# Example usage
if __name__ == "__main__":
    # Initialize processor
    processor = NLPProcessor()
    
    # Test messages
    test_messages = [
        "สวัสดีค่ะ น้องอุ่นใจ",
        "วันนี้รู้สึกนอยๆ ตั้งแต่เช้า",
        "อยากตาย ไม่อยากอยู่แล้ว",
        "พระเจ้ามีจริงปะ?",
        "ขอคลิปหนุนใจหน่อย",
        "ตอบ ข้อ A ค่ะ",
    ]
    
    print("=" * 70)
    print("🧠 NLP Processor Test Results")
    print("=" * 70)
    
    for msg in test_messages:
        result = processor.analyze(msg)
        
        print(f"\n📝 Input: {msg}")
        print(f"   Sentiment: {result.sentiment.label.name} ({result.sentiment.score:.2f})")
        print(f"   Intent: {result.intent.primary_intent.value}")
        print(f"   Crisis: {result.crisis.level.name}")
        print(f"   R-Score: {result.r_score:.1f}")
        print(f"   Persona: {result.recommended_persona}")
        print(f"   Time: {result.processing_time_ms}ms")
