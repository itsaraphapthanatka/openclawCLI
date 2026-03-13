# Nong Unjai AI - Docker Deployment

## 🐳 Quick Start

```bash
# 1. Clone and setup
cd nong-unjai-ai

# 2. Create environment file
cp .env.example .env
# Edit .env with your credentials

# 3. Start all services
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f
```

## 📁 Services

| Service | Port | Description |
|---------|------|-------------|
| `line-gateway` | 8000 | LINE Webhook API |
| `orchestrator` | 8001 | Main controller (internal) |
| `analytics` | 8002 | Dashboard API |
| `qa-tester` | - | QA testing (on-demand) |
| `postgres` | 5432 | PostgreSQL database |
| `redis` | 6379 | Session & cache |
| `nginx` | 80/443 | Reverse proxy |

## 🔧 Environment Variables

```env
# LINE Bot
LINE_CHANNEL_SECRET=your_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_channel_token

# OpenAI
OPENAI_API_KEY=your_openai_key

# Pinecone
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env
PINECONE_INDEX_NAME=unjai-knowledge

# Database
POSTGRES_USER=unjai
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=unjai

# Redis
REDIS_PASSWORD=your_redis_password

# Middleware
MIDDLEWARE_URL=http://middleware:8080
```

## 📊 Architecture

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
┌──────▼──────┐
│    LINE     │
└──────┬──────┘
       │
┌──────▼──────┐     ┌─────────────┐
│    Nginx    │────▶│  Analytics  │:8002
└──────┬──────┘     └─────────────┘
       │
┌──────▼────────┐   ┌─────────────┐
│  LINE Gateway │──▶│    Redis    │
│    :8000      │   │   (Cache)   │
└──────┬────────┘   └─────────────┘
       │
┌──────▼────────┐   ┌─────────────┐
│ Orchestrator  │──▶│  PostgreSQL │
│    :8001      │   │  (Data)     │
└──────┬────────┘   └─────────────┘
       │
┌──────┴────────┐
│   Modules     │
│ 1. The Brain  │◄──▶ Pinecone
│ 2. NLP        │
│ 5. Coins      │
│ 8. Nudge      │
│ 10. QA        │
│ 11. Trends    │
└───────────────┘
```

## 🛠️ Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart service
docker-compose restart line-gateway

# View logs
docker-compose logs -f line-gateway

# Update images
docker-compose pull && docker-compose up -d

# Clean rebuild
docker-compose down -v
docker-compose up -d --build
```

## 📈 Monitoring

- Analytics Dashboard: http://localhost:8002/dashboard
- Health Check: http://localhost:8000/health
- Prometheus metrics: http://localhost:8000/metrics

## 🚀 Production Deployment

```bash
# Production compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# With SSL (Let's Encrypt)
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d
```
