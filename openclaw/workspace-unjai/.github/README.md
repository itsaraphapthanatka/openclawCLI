# CI/CD Pipeline

## 🎯 Overview

GitHub Actions workflows สำหรับ:
- **Build & Test** - ตรวจสอบคุณภาพโค้ด
- **Docker Build** - สร้าง Docker images
- **Deploy** - Deploy ไปยัง staging/production
- **QA** - รัน automated tests

## 🚀 Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | PR, Push | Test, lint, build |
| `docker-build.yml` | Push to main | Build & push images |
| `deploy-staging.yml` | Tag `v*-rc*` | Deploy to staging |
| `deploy-prod.yml` | Tag `v*` | Deploy to production |
| `qa-nightly.yml` | Cron 3 AM | Nightly QA tests |

## 📋 Prerequisites

### GitHub Secrets

```
DOCKER_USERNAME
DOCKER_PASSWORD
KUBE_CONFIG_STAGING
KUBE_CONFIG_PRODUCTION
LINE_CHANNEL_SECRET_STAGING
LINE_CHANNEL_TOKEN_STAGING
LINE_CHANNEL_SECRET_PROD
LINE_CHANNEL_TOKEN_PROD
OPENAI_API_KEY
PINECONE_API_KEY
```

## 🔄 Pipeline Flow

```
Developer
    │
    ▼
Pull Request ──▶ CI (test, lint)
    │
    ▼
Merge to main ──▶ Docker Build ──▶ Push to Registry
    │
    ▼
Tag v1.0.0-rc1 ──▶ Deploy Staging
    │
    ▼
Tag v1.0.0 ──▶ Deploy Production
```

## 📊 Status Badges

```markdown
![CI](https://github.com/your-org/nong-unjai/actions/workflows/ci.yml/badge.svg)
![Docker](https://github.com/your-org/nong-unjai/actions/workflows/docker-build.yml/badge.svg)
![Deploy](https://github.com/your-org/nong-unjai/actions/workflows/deploy-prod.yml/badge.svg)
```
