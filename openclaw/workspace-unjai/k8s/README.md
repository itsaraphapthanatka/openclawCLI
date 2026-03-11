# Kubernetes Deployment

## 🎯 Quick Start

```bash
# 1. Setup namespace
kubectl apply -f k8s/00-namespace.yaml

# 2. Create secrets
kubectl create secret generic unjai-secrets \
  --from-literal=line-channel-secret=xxx \
  --from-literal=line-channel-token=xxx \
  --from-literal=openai-api-key=xxx \
  --from-literal=postgres-password=xxx \
  --from-literal=redis-password=xxx \
  --namespace=unjai

# 3. Deploy database
kubectl apply -f k8s/01-postgres.yaml
kubectl apply -f k8s/02-redis.yaml

# 4. Deploy applications
kubectl apply -f k8s/10-configmap.yaml
kubectl apply -f k8s/20-orchestrator.yaml
kubectl apply -f k8s/21-analytics.yaml
kubectl apply -f k8s/22-nudge.yaml
kubectl apply -f k8s/23-trends.yaml
kubectl apply -f k8s/30-gateway.yaml

# 5. Deploy ingress
kubectl apply -f k8s/40-ingress.yaml

# 6. Check status
kubectl get pods -n unjai
kubectl get svc -n unjai
kubectl get ingress -n unjai
```

## 📁 File Structure

```
k8s/
├── 00-namespace.yaml      # Namespace
├── 01-postgres.yaml       # PostgreSQL StatefulSet
├── 02-redis.yaml          # Redis Deployment
├── 10-configmap.yaml      # ConfigMap
├── 20-orchestrator.yaml   # Orchestrator Deployment
├── 21-analytics.yaml      # Analytics Deployment
├── 22-nudge.yaml          # Nudge Scheduler CronJob
├── 23-trends.yaml         # Trend Predictor CronJob
├── 30-gateway.yaml        # LINE Gateway Deployment
└── 40-ingress.yaml        # Ingress (NGINX)
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Ingress (HTTPS)                     │
│                   nginx-ingress-controller               │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Gateway    │  │  Analytics   │  │   Webhook    │
│   (LINE)     │  │  (Dashboard) │  │              │
└──────┬───────┘  └──────────────┘  └──────────────┘
       │
       ▼
┌──────────────┐
│ Orchestrator │◄──────┬────────┬────────┬────────┐
└──────────────┘       │        │        │        │
                       ▼        ▼        ▼        ▼
                 ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
                 │Module 1│ │Module 2│ │Module 5│ │Module 8│
                 │Module 9│ │Module10│ │Module11│ │        │
                 └────────┘ └────────┘ └────────┘ └────────┘
                       │        │        │        │
                       └────────┴────────┴────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
            ┌──────────────┐          ┌──────────────┐
            │   Postgres   │          │    Redis     │
            │  (Stateful)  │          │   (Cache)    │
            └──────────────┘          └──────────────┘
```

## 📋 Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- NGINX Ingress Controller
- Cert-Manager (for SSL)
- PV provisioner (for Postgres)

## 🔧 Installation

### 1. Install NGINX Ingress

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

### 2. Install Cert-Manager

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### 3. Create ClusterIssuer

```bash
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 4. Deploy Application

```bash
kubectl apply -f k8s/
```

## 📊 Monitoring

```bash
# Watch pods
kubectl get pods -n unjai -w

# Check logs
kubectl logs -f deployment/gateway -n unjai

# Scale
kubectl scale deployment gateway --replicas=3 -n unjai

# Port forward for testing
kubectl port-forward svc/gateway 8000:8000 -n unjai
```

## 🚀 Updates

```bash
# Rolling update
kubectl set image deployment/gateway \
  gateway=nong-unjai/gateway:v2.0.0 -n unjai

# Rollback
kubectl rollout undo deployment/gateway -n unjai
```
