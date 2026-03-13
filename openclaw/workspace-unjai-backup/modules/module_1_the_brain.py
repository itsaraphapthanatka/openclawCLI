"""
Module 1: The Brain - Knowledge Base & Vector DB
Nong Unjai AI System

This module handles:
- Vector database operations (Pinecone)
- Embedding generation and storage
- Semantic search for video content
- 3 Circles content classification
- Integration with PostgreSQL for metadata

Tech Stack:
- Pinecone (Vector Database)
- OpenAI/HuggingFace (Embeddings)
- PostgreSQL (Metadata storage)
- Redis (Caching)
"""

import os
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

import pinecone
from pinecone import Pinecone, ServerlessSpec
import openai
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircleLevel(Enum):
    """3 Circles Logic - Content classification"""
    SELF = 1        # การรักตัวเอง (Self-love, healing, identity)
    CLOSE_ONES = 2  # ความสัมพันธ์คนใกล้ชิด (Family, friends, relationships)
    SOCIETY = 3     # การอยู่ร่วมกับสังคม (Community, volunteering, social impact)


@dataclass
class VideoMetadata:
    """Metadata structure for video content"""
    video_id: str
    youtube_url: str
    title: str
    description: str
    transcript: str
    summary: str
    duration_seconds: int
    circle_level: CircleLevel
    topic_tags: List[str]
    scripture_refs: List[Dict[str, Any]]  # [{"book": "John", "chapter": 3, "verse": "16"}]
    tone: str  # gentle, energetic, urgent, comforting
    pastor_name: Optional[str] = None
    church_name: Optional[str] = None
    language: str = "th"
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['circle_level'] = self.circle_level.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data


@dataclass
class SearchResult:
    """Structure for search results"""
    video_id: str
    score: float
    metadata: VideoMetadata
    matched_segments: List[Dict[str, Any]]  # [{"start": 120, "end": 180, "text": "..."}]
    relevance_explanation: str


class EmbeddingGenerator:
    """
    Agent: Archivist
    Task: Generate embeddings for text content
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small", dimensions: int = 384):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.dimensions = dimensions  # Match Pinecone index dimension (384 for aunjai-knowledge)
        self.client = openai.OpenAI(api_key=self.api_key)
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        try:
            # Clean and truncate text
            text = text.strip()[:8000]  # OpenAI limit
            
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dimensions  # Truncate to match Pinecone index dimension
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding with dimension: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = self.generate(text)
            embeddings.append(embedding)
        return embeddings


class VectorDatabase:
    """
    Agent: Search Specialist + Archivist
    Task: Manage Pinecone vector database operations
    
    Configuration (from environment variables):
    - PINECONE_API_KEY: API key for Pinecone
    - PINECONE_INDEX_NAME: Index name (default: aunjai-knowledge)
    - PINECONE_INDEX_HOST: Index host URL
    - PINECONE_NAMESPACE: Namespace for data (default: highlights)
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 index_name: Optional[str] = None,
                 index_host: Optional[str] = None,
                 namespace: Optional[str] = None,
                 dimension: int = 384):  # Match aunjai-knowledge index dimension
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "aunjai-knowledge")
        self.index_host = index_host or os.getenv("PINECONE_INDEX_HOST", "https://aunjai-knowledge-3ygam8j.svc.aped-4627-b74a.pinecone.io")
        self.namespace = namespace or os.getenv("PINECONE_NAMESPACE", "highlights")
        self.dimension = dimension
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        self.index = self._get_index_with_namespace()
        
    def _get_index_with_namespace(self):
        """Get existing index with namespace"""
        try:
            # Connect to existing index using host
            index = self.pc.Index(name=self.index_name, host=self.index_host)
            logger.info(f"Connected to Pinecone index: {self.index_name} (namespace: {self.namespace})")
            return index
            
        except Exception as e:
            logger.error(f"Error connecting to index: {e}")
            raise
    
    def _get_namespace_index(self):
        """Get index scoped to namespace"""
        return self.index
    
    def upsert_video(self, 
                     video_metadata: VideoMetadata,
                     embedding: List[float],
                     chunk_id: Optional[str] = None) -> bool:
        """
        Insert or update video content in vector DB
        
        Args:
            video_metadata: Video metadata
            embedding: Vector embedding of transcript/summary
            chunk_id: Optional chunk ID for long videos (format: video_id_chunk_001)
        """
        try:
            # Generate unique ID
            if chunk_id:
                vector_id = chunk_id
            else:
                vector_id = video_metadata.video_id
            
            # Prepare metadata (Pinecone has limits on metadata size)
            metadata = {
                "video_id": video_metadata.video_id,
                "title": video_metadata.title[:500],  # Truncate for size limit
                "description": video_metadata.description[:1000],
                "summary": video_metadata.summary[:1000],
                "duration": video_metadata.duration_seconds,
                "circle_level": video_metadata.circle_level.value,
                "tone": video_metadata.tone,
                "topic_tags": json.dumps(video_metadata.topic_tags[:20]),  # Limit tags
                "scripture_refs": json.dumps(video_metadata.scripture_refs[:5]),
                "pastor_name": video_metadata.pastor_name,
                "language": video_metadata.language,
                "created_at": video_metadata.created_at.isoformat()
            }
            
            # Upsert to Pinecone with namespace
            self.index.upsert(
                vectors=[{
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                }],
                namespace=self.namespace
            )
            
            logger.info(f"Upserted video to namespace '{self.namespace}': {vector_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting video: {e}")
            return False
    
    def search(self, 
               query_embedding: List[float],
               circle_level: Optional[CircleLevel] = None,
               top_k: int = 5,
               filter_tags: Optional[List[str]] = None) -> List[SearchResult]:
        """
        Semantic search for videos
        
        Args:
            query_embedding: Query vector
            circle_level: Filter by 3 Circles (1, 2, or 3)
            top_k: Number of results
            filter_tags: Filter by topic tags
            
        Returns:
            List of SearchResult objects
        """
        try:
            # Build filter
            filter_dict = {}
            if circle_level:
                filter_dict["circle_level"] = {"$eq": circle_level.value}
            if filter_tags:
                # Note: Pinecone doesn't support array contains directly
                # We'll filter post-query or use metadata string matching
                pass
            
            # Query Pinecone with namespace
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None,
                namespace=self.namespace
            )
            
            # Convert to SearchResult objects
            search_results = []
            for match in results.matches:
                metadata = match.metadata
                
                # Reconstruct VideoMetadata
                video_metadata = VideoMetadata(
                    video_id=metadata.get("video_id"),
                    youtube_url="",  # Will be fetched from PostgreSQL
                    title=metadata.get("title", ""),
                    description=metadata.get("description", ""),
                    transcript="",  # Full transcript in PostgreSQL
                    summary=metadata.get("summary", ""),
                    duration_seconds=metadata.get("duration", 0),
                    circle_level=CircleLevel(metadata.get("circle_level", 1)),
                    topic_tags=json.loads(metadata.get("topic_tags", "[]")),
                    scripture_refs=json.loads(metadata.get("scripture_refs", "[]")),
                    tone=metadata.get("tone", "gentle"),
                    pastor_name=metadata.get("pastor_name"),
                    language=metadata.get("language", "th")
                )
                
                result = SearchResult(
                    video_id=metadata.get("video_id"),
                    score=match.score,
                    metadata=video_metadata,
                    matched_segments=[],
                    relevance_explanation=f"Semantic similarity score: {match.score:.3f}"
                )
                search_results.append(result)
            
            logger.info(f"Search returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def delete_video(self, video_id: str) -> bool:
        """Delete video from vector DB"""
        try:
            self.index.delete(ids=[video_id])
            logger.info(f"Deleted video: {video_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting video: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
        return self.index.describe_index_stats()


class MetadataStore:
    """
    Agent: Archivist
    Task: Store and retrieve video metadata in PostgreSQL
    """
    
    def __init__(self, 
                 host: Optional[str] = None,
                 database: Optional[str] = None,
                 user: Optional[str] = None,
                 password: Optional[str] = None,
                 port: int = 5432):
        self.connection_params = {
            "host": host or os.getenv("POSTGRES_HOST", "localhost"),
            "database": database or os.getenv("POSTGRES_DB", "nong_unjai"),
            "user": user or os.getenv("POSTGRES_USER", "postgres"),
            "password": password or os.getenv("POSTGRES_PASSWORD", ""),
            "port": port
        }
        
        self._init_tables()
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.connection_params)
    
    def _init_tables(self):
        """Initialize database tables"""
        create_tables_sql = """
        -- Videos table
        CREATE TABLE IF NOT EXISTS videos (
            id SERIAL PRIMARY KEY,
            video_id VARCHAR(50) UNIQUE NOT NULL,
            youtube_url TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            transcript TEXT,
            summary TEXT,
            duration_seconds INTEGER,
            circle_level INTEGER CHECK (circle_level IN (1, 2, 3)),
            topic_tags TEXT[],
            scripture_refs JSONB,
            tone VARCHAR(50),
            pastor_name VARCHAR(255),
            church_name VARCHAR(255),
            language VARCHAR(10) DEFAULT 'th',
            pinecone_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Video chunks for long videos
        CREATE TABLE IF NOT EXISTS video_chunks (
            id SERIAL PRIMARY KEY,
            chunk_id VARCHAR(100) UNIQUE NOT NULL,
            video_id VARCHAR(50) REFERENCES videos(video_id) ON DELETE CASCADE,
            start_time INTEGER NOT NULL,
            end_time INTEGER NOT NULL,
            transcript TEXT,
            summary TEXT,
            embedding_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Search logs for analytics
        CREATE TABLE IF NOT EXISTS search_logs (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(100),
            query_text TEXT,
            query_embedding_id VARCHAR(100),
            results_count INTEGER,
            top_result_id VARCHAR(50),
            circle_filter INTEGER,
            response_time_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_videos_circle ON videos(circle_level);
        CREATE INDEX IF NOT EXISTS idx_videos_tags ON videos USING GIN(topic_tags);
        CREATE INDEX IF NOT EXISTS idx_videos_video_id ON videos(video_id);
        CREATE INDEX IF NOT EXISTS idx_chunks_video ON video_chunks(video_id);
        """
        
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute(create_tables_sql)
                conn.commit()
            logger.info("Database tables initialized")
        except Exception as e:
            logger.error(f"Error initializing tables: {e}")
        finally:
            if conn:
                conn.close()
    
    def save_video(self, video_metadata: VideoMetadata, pinecone_id: str) -> bool:
        """Save video metadata to PostgreSQL"""
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO videos (
                        video_id, youtube_url, title, description, transcript,
                        summary, duration_seconds, circle_level, topic_tags,
                        scripture_refs, tone, pastor_name, church_name, language, pinecone_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (video_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        transcript = EXCLUDED.transcript,
                        summary = EXCLUDED.summary,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    video_metadata.video_id,
                    video_metadata.youtube_url,
                    video_metadata.title,
                    video_metadata.description,
                    video_metadata.transcript,
                    video_metadata.summary,
                    video_metadata.duration_seconds,
                    video_metadata.circle_level.value,
                    video_metadata.topic_tags,
                    json.dumps(video_metadata.scripture_refs),
                    video_metadata.tone,
                    video_metadata.pastor_name,
                    video_metadata.church_name,
                    video_metadata.language,
                    pinecone_id
                ))
                conn.commit()
                logger.info(f"Saved video metadata: {video_metadata.video_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving video: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_video(self, video_id: str) -> Optional[VideoMetadata]:
        """Retrieve video metadata by ID"""
        try:
            conn = self._get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM videos WHERE video_id = %s", (video_id,))
                row = cur.fetchone()
                
                if row:
                    return VideoMetadata(
                        video_id=row['video_id'],
                        youtube_url=row['youtube_url'],
                        title=row['title'],
                        description=row['description'],
                        transcript=row['transcript'],
                        summary=row['summary'],
                        duration_seconds=row['duration_seconds'],
                        circle_level=CircleLevel(row['circle_level']),
                        topic_tags=row['topic_tags'] or [],
                        scripture_refs=row['scripture_refs'] or [],
                        tone=row['tone'],
                        pastor_name=row['pastor_name'],
                        church_name=row['church_name'],
                        language=row['language'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving video: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def search_by_tags(self, tags: List[str], circle_level: Optional[CircleLevel] = None) -> List[VideoMetadata]:
        """Search videos by tags (fallback when semantic search not available)"""
        try:
            conn = self._get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if circle_level:
                    cur.execute("""
                        SELECT * FROM videos 
                        WHERE topic_tags && %s AND circle_level = %s
                        ORDER BY created_at DESC
                        LIMIT 20
                    """, (tags, circle_level.value))
                else:
                    cur.execute("""
                        SELECT * FROM videos 
                        WHERE topic_tags && %s
                        ORDER BY created_at DESC
                        LIMIT 20
                    """, (tags,))
                
                rows = cur.fetchall()
                videos = []
                for row in rows:
                    videos.append(VideoMetadata(
                        video_id=row['video_id'],
                        youtube_url=row['youtube_url'],
                        title=row['title'],
                        description=row['description'],
                        transcript=row['transcript'],
                        summary=row['summary'],
                        duration_seconds=row['duration_seconds'],
                        circle_level=CircleLevel(row['circle_level']),
                        topic_tags=row['topic_tags'] or [],
                        scripture_refs=row['scripture_refs'] or [],
                        tone=row['tone'],
                        pastor_name=row['pastor_name'],
                        church_name=row['church_name'],
                        language=row['language']
                    ))
                return videos
                
        except Exception as e:
            logger.error(f"Error searching by tags: {e}")
            return []
        finally:
            if conn:
                conn.close()


class KnowledgeBase:
    """
    Main interface combining all components
    Agent: The Brain (Orchestrator)
    """
    
    def __init__(self):
        self.embedding_gen = EmbeddingGenerator()
        self.vector_db = VectorDatabase()
        self.metadata_store = MetadataStore()
        
        # Redis for caching
        self.cache = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True
        )
    
    def add_video(self, video_metadata: VideoMetadata) -> bool:
        """
        Add new video to knowledge base
        
        Flow:
        1. Generate embedding from transcript/summary
        2. Save to Pinecone (vector DB)
        3. Save metadata to PostgreSQL
        """
        try:
            # Generate embedding
            text_to_embed = f"{video_metadata.title}\n{video_metadata.summary}\n{video_metadata.transcript[:2000]}"
            embedding = self.embedding_gen.generate(text_to_embed)
            
            # Save to vector DB
            success = self.vector_db.upsert_video(video_metadata, embedding)
            if not success:
                return False
            
            # Save metadata
            pinecone_id = video_metadata.video_id
            self.metadata_store.save_video(video_metadata, pinecone_id)
            
            # Clear cache
            self.cache.delete(f"search:{video_metadata.circle_level.value}:*")
            
            logger.info(f"Successfully added video: {video_metadata.video_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding video: {e}")
            return False
    
    def search(self, 
               query: str,
               user_circle_level: Optional[CircleLevel] = None,
               user_id: Optional[str] = None,
               top_k: int = 5) -> List[SearchResult]:
        """
        Search for relevant videos
        
        Args:
            query: User's question or emotional expression
            user_circle_level: Current circle level of user (for personalization)
            user_id: For logging
            top_k: Number of results
        """
        start_time = datetime.now()
        
        try:
            # Check cache
            cache_key = f"search:{query}:{user_circle_level}:{top_k}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.info("Cache hit for search query")
                return json.loads(cached)
            
            # Generate query embedding
            query_embedding = self.embedding_gen.generate(query)
            
            # Determine which circle to search
            # If user is in Circle 1, show Circle 1 content primarily
            # But also include some Circle 2 for growth
            search_circle = user_circle_level
            
            # Search vector DB
            results = self.vector_db.search(
                query_embedding=query_embedding,
                circle_level=search_circle,
                top_k=top_k
            )
            
            # If not enough results, search without circle filter
            if len(results) < top_k:
                additional_results = self.vector_db.search(
                    query_embedding=query_embedding,
                    circle_level=None,
                    top_k=top_k - len(results)
                )
                # Filter out duplicates
                existing_ids = {r.video_id for r in results}
                for r in additional_results:
                    if r.video_id not in existing_ids:
                        results.append(r)
            
            # Enrich with full metadata from PostgreSQL
            for result in results:
                full_metadata = self.metadata_store.get_video(result.video_id)
                if full_metadata:
                    result.metadata = full_metadata
            
            # Log search
            self._log_search(user_id, query, len(results), user_circle_level)
            
            # Cache results (5 minutes)
            self.cache.setex(cache_key, 300, json.dumps([{
                'video_id': r.video_id,
                'score': r.score,
                'metadata': r.metadata.to_dict() if r.metadata else None,
                'relevance_explanation': r.relevance_explanation
            } for r in results]))
            
            return results
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return []
    
    def get_recommendations(self, 
                           user_circle_level: CircleLevel,
                           watched_videos: List[str],
                           mood: Optional[str] = None) -> List[SearchResult]:
        """
        Get personalized recommendations based on user state
        
        Used by Journey Architect for Circle progression
        """
        try:
            # Build query based on mood and circle
            query_parts = []
            
            if mood == "sad" or mood == "depressed":
                query_parts.append("comfort hope healing encouragement")
            elif mood == "anxious" or mood == "worried":
                query_parts.append("peace calm trust faith")
            elif mood == "angry":
                query_parts.append("forgiveness peace patience")
            else:
                query_parts.append("inspiration growth faith")
            
            # Add circle-specific keywords
            if user_circle_level == CircleLevel.SELF:
                query_parts.append("self-love identity worth acceptance")
            elif user_circle_level == CircleLevel.CLOSE_ONES:
                query_parts.append("relationship family love communication")
            elif user_circle_level == CircleLevel.SOCIETY:
                query_parts.append("community service purpose calling")
            
            query = " ".join(query_parts)
            
            # Search
            results = self.search(
                query=query,
                user_circle_level=user_circle_level,
                top_k=5
            )
            
            # Filter out already watched
            results = [r for r in results if r.video_id not in watched_videos]
            
            return results[:3]  # Top 3 recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    def _log_search(self, user_id: Optional[str], query: str, 
                    results_count: int, circle_filter: Optional[CircleLevel]):
        """Log search for analytics"""
        try:
            conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                database=os.getenv("POSTGRES_DB", "nong_unjai"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "")
            )
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO search_logs 
                    (user_id, query_text, results_count, circle_filter)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, query, results_count, 
                     circle_filter.value if circle_filter else None))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging search: {e}")
        finally:
            if conn:
                conn.close()
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        return {
            "vector_db": self.vector_db.get_stats(),
            "cache_status": "connected" if self.cache.ping() else "disconnected"
        }


# Utility functions for content processing
def chunk_transcript(transcript: str, chunk_size: int = 400, overlap: int = 50) -> List[Dict]:
    """
    Split transcript into semantic chunks
    
    Args:
        transcript: Full transcript text
        chunk_size: Target chunk size (characters)
        overlap: Overlap between chunks
        
    Returns:
        List of chunks with start/end times (estimated)
    """
    chunks = []
    words = transcript.split()
    
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1
        
        if current_size >= chunk_size:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "char_count": len(chunk_text)
            })
            
            # Keep overlap words for next chunk
            overlap_words = current_chunk[-overlap//10:] if len(current_chunk) > overlap//10 else []
            current_chunk = overlap_words
            current_size = sum(len(w) for w in current_chunk)
    
    # Add remaining chunk
    if current_chunk:
        chunks.append({
            "text": " ".join(current_chunk),
            "char_count": current_size
        })
    
    return chunks


def extract_scripture_references(text: str) -> List[Dict]:
    """
    Extract Bible scripture references from text
    
    Examples:
        "ยอห์น 3:16" -> {"book": "John", "chapter": 3, "verse": "16"}
        "สดุดี 23:1-6" -> {"book": "Psalms", "chapter": 23, "verse": "1-6"}
    """
    import re
    
    # Thai book names mapping
    thai_to_english = {
        " Genesis": "Genesis",
        "อพยพ": "Exodus",
        "เลวีนิติ": "Leviticus",
        "กันดารวิถี": "Numbers",
        "เฉลยธรรมบัญญัติ": "Deuteronomy",
        "โยชูวา": "Joshua",
        "สดุดี": "Psalms",
        "สุภาษิต": "Proverbs",
        "ยอห์น": "John",
        "โรม": "Romans",
        "1 โครินธ์": "1 Corinthians",
        "2 โครินธ์": "2 Corinthians",
        "กาลาเทีย": "Galatians",
        "เอเฟซัส": "Ephesians",
        "ฟิลิปปี": "Philippians",
        "โคโลสี": "Colossians",
        "1 เธสะโลนิกา": "1 Thessalonians",
        "2 เธสะโลนิกา": "2 Thessalonians",
        "1 ทิโมธี": "1 Timothy",
        "2 ทิโมธี": "2 Timothy",
        "ติตัส": "Titus",
        "ฟีเลโมน": "Philemon",
        "ฮีบรู": "Hebrews",
        "ยากอบ": "James",
        "1 เปโตร": "1 Peter",
        "2 เปโตร": "2 Peter",
        "1 ยอห์น": "1 John",
        "2 ยอห์น": "2 John",
        "3 ยอห์น": "3 John",
        "ยูดา": "Jude",
        "วิวรณ์": "Revelation"
    }
    
    references = []
    
    # Pattern for Thai scripture references
    # Examples: "ยอห์น 3:16", "สดุดี 23:1-6", "โรม 8:28-39"
    pattern = r'(\S+)\s+(\d+):(\d+(?:-\d+)?)'
    
    matches = re.finditer(pattern, text)
    for match in matches:
        thai_book = match.group(1)
        chapter = int(match.group(2))
        verse = match.group(3)
        
        english_book = thai_to_english.get(thai_book, thai_book)
        
        references.append({
            "book": english_book,
            "thai_book": thai_book,
            "chapter": chapter,
            "verse": verse,
            "full_reference": f"{thai_book} {chapter}:{verse}"
        })
    
    return references


# Example usage and testing
if __name__ == "__main__":
    # Initialize knowledge base
    kb = KnowledgeBase()
    
    # Example: Add a video
    video = VideoMetadata(
        video_id="yt_video_001",
        youtube_url="https://youtube.com/watch?v=example",
        title="การรักตัวเองตามพระคัมภีร์",
        description="คำสอนเกี่ยวกับการเห็นคุณค่าในตัวเอง",
        transcript="พระเจ้าทรงสร้างมนุษย์ตามพระฉายของพระองค์...",
        summary="คำสอนเรื่อง self-worth และการรักตัวเอง",
        duration_seconds=600,
        circle_level=CircleLevel.SELF,
        topic_tags=["self-love", "identity", "healing"],
        scripture_refs=[{"book": "Genesis", "chapter": 1, "verse": "27"}],
        tone="gentle",
        pastor_name=" Pastor John",
        language="th"
    )
    
    # Add to knowledge base
    success = kb.add_video(video)
    print(f"Added video: {success}")
    
    # Search
    results = kb.search("รู้สึกไม่มีค่า อยากได้กำลังใจ", user_circle_level=CircleLevel.SELF)
    for r in results:
        print(f"- {r.metadata.title} (score: {r.score:.3f})")
    
    # Get stats
    print(kb.get_stats())
