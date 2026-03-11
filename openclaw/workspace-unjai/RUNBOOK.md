# Nong Unjai AI - Production Runbook

## 🚀 Quick Start Production Deployment

```bash
# 1. Clone repository
git clone https://github.com/your-org/nong-unjai-ai.git
cd nong-unjai-ai

# 2. Set environment variables
export DOMAIN=nong-unjai.yourdomain.com
export VERSION=v1.0.0

# 3. Create secrets
kubectl create secret generic unjai-secrets \
  --from-literal=line-channel-secret=$LINE_CHANNEL_SECRET \
  --from-literal=line-channel-token=$LINE_CHANNEL_TOKEN \
  --from-literal=openai-api-key=$OPENAI_API_KEY \
  --from-literal=pinecone-api-key=$PINECONE_API_KEY \
  --from-literal=postgres-password=$(openssl rand -base64 32) \
  --from-literal=redis-password=$(openssl rand -base64 32) \
  --namespace=unjai

# 4. Deploy everything
./deploy-production.sh production all
```

## 📋 Production Checklist

### Pre-Deployment

- [ ] Domain configured with DNS A record
- [ ] SSL certificate obtained (Let's Encrypt)
- [ ] Kubernetes cluster provisioned
- [ ] Secrets created
- [ ] Resource quotas defined
- [ ] Backup strategy configured

### Deployment

- [ ] Database deployed and healthy
- [ ] All applications deployed
- [ ] Ingress configured
- [ ] SSL working (HTTPS)
- [ ] Health checks passing
- [ ] Monitoring deployed
- [ ] Alerts configured

### Post-Deployment

- [ ] LINE webhook URL configured
- [ ] Test message received
- [ ] Crisis detection tested
- [ ] Analytics dashboard accessible
- [ ] Grafana login working
- [ ] Alerts firing correctly

## 🔧 Common Operations

### View Logs

```bash
# Gateway logs
kubectl logs -f deployment/gateway -n unjai

# All pods
kubectl logs -f -l app=gateway -n unjai --all-containers

# Previous container (if crashed)
kubectl logs deployment/gateway -n unjai --previous
```

### Scale Services

```bash
# Scale gateway to 3 replicas
kubectl scale deployment gateway --replicas=3 -n unjai

# Scale orchestrator
kubectl scale deployment orchestrator --replicas=5 -n unjai

# Autoscale (HPA)
kubectl autoscale deployment gateway --min=2 --max=10 --cpu-percent=70 -n unjai
```

### Update Version

```bash
# Rolling update
kubectl set image deployment/gateway \
  gateway=ghcr.io/your-org/nong-unjai/gateway:v1.1.0 -n unjai

# Watch rollout
kubectl rollout status deployment/gateway -n unjai

# Rollback if needed
kubectl rollout undo deployment/gateway -n unjai
```

### Database Backup

```bash
# Backup PostgreSQL
kubectl exec -it postgres-0 -n unjai -- pg_dump -U unjai unjai > backup.sql

# Restore
kubectl exec -i postgres-0 -n unjai -- psql -U unjai unjai < backup.sql
```

## 🚨 Troubleshooting

### Pod Not Starting

```bash
# Check events
kubectl describe pod <pod-name> -n unjai

# Check logs
kubectl logs <pod-name> -n unjai

# Check resources
kubectl top pod <pod-name> -n unjai
```

### High Error Rate

```bash
# Check gateway errors
kubectl logs -l app=gateway -n unjai | grep ERROR

# Restart gateway
kubectl rollout restart deployment/gateway -n unjai
```

### Database Connection Issues

```bash
# Test connection
kubectl exec -it postgres-0 -n unjai -- psql -U unjai -c "SELECT 1;"

# Check service
kubectl get svc postgres -n unjai
```

## 📊 Monitoring

### Access Dashboards

```bash
# Grafana
kubectl port-forward svc/grafana 3000:3000 -n monitoring
# http://localhost:3000 (admin/admin)

# Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
# http://localhost:9090
```

### Key Metrics

| Metric | Threshold | Action |
|--------|-----------|--------|
| Error Rate | > 5% | Investigate logs |
| P99 Latency | > 500ms | Scale up |
| CPU Usage | > 80% | Scale horizontally |
| Memory Usage | > 85% | Increase limits |
| Crisis Incidents | > 10/hour | Alert volunteers |

## 🔐 Security

### Rotate Secrets

```bash
# Update LINE token
kubectl create secret generic unjai-secrets \
  --from-literal=line-channel-token=$NEW_TOKEN \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart to pick up new secret
kubectl rollout restart deployment/gateway -n unjai
```

### Network Policies

```bash
# Apply network policy
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: unjai
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
EOF
```

## 📞 Emergency Contacts

- **On-call Engineer**: [Your contact]
- **LINE Dev Support**: [LINE contact]
- **Infra Team**: [Infra contact]

## 📝 Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2024-02-27 | v1.0.0 | Initial production deployment |
