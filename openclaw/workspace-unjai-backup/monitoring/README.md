# Monitoring Stack: Prometheus + Grafana

## 🎯 Quick Start

```bash
# Deploy monitoring stack
kubectl apply -f monitoring/namespace.yaml
kubectl apply -f monitoring/prometheus/
kubectl apply -f monitoring/grafana/

# Access Grafana
kubectl port-forward svc/grafana 3000:3000 -n monitoring
# Open http://localhost:3000
# Default: admin/admin
```

## 📊 Dashboards Included

| Dashboard | Metrics |
|-----------|---------|
| Nong UnjAI Overview | Requests, latency, errors |
| System Health | CPU, memory, disk |
| NLP Metrics | Sentiment, intent classification |
| Coin Economy | Transactions, balances |
| Crisis Detection | Incidents, response times |

## 🔍 Available Metrics

```
# Application Metrics
unjai_requests_total{path="/webhook", status="200"}
unjai_request_duration_seconds_bucket{path="/webhook"}
unjai_active_users
unjai_crisis_incidents_total
unjai_sentiment_score_sum
unjai_coins_earned_total

# System Metrics
process_cpu_seconds_total
process_resident_memory_bytes
python_gc_objects_collected_total
```

## 📈 Alerts

| Alert | Condition | Action |
|-------|-----------|--------|
| HighErrorRate | > 5% errors | Page on-call |
| HighLatency | p99 > 500ms | Slack warning |
| CrisisSpike | > 10 incidents/hour | Emergency alert |
| ServiceDown | health check fails | Page on-call |

## 🚀 Accessing

```bash
# Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
# http://localhost:9090

# Grafana
kubectl port-forward svc/grafana 3000:3000 -n monitoring
# http://localhost:3000
```
