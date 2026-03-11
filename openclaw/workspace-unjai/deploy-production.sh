#!/bin/bash
# Nong Unjai AI - Production Deployment Script
# Usage: ./deploy-production.sh [environment]

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENV=${1:-production}
NAMESPACE="unjai"
DOMAIN=${DOMAIN:-nong-unjai.example.com}
VERSION=${VERSION:-latest}

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_banner() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║           Nong Unjai AI - Production Deployment              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    log_info "Environment: $ENV"
    log_info "Namespace: $NAMESPACE"
    log_info "Domain: $DOMAIN"
    log_info "Version: $VERSION"
    echo ""
}

# Pre-deployment checks
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl."
        exit 1
    fi
    log_success "kubectl installed"
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    log_success "Connected to Kubernetes cluster"
    
    # Check namespace
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        log_warn "Namespace $NAMESPACE not found. Creating..."
        kubectl create namespace $NAMESPACE
    fi
    log_success "Namespace $NAMESPACE ready"
    
    # Check secrets
    if ! kubectl get secret unjai-secrets -n $NAMESPACE &> /dev/null; then
        log_warn "Secrets not found. Please create secrets first:"
        echo "  kubectl create secret generic unjai-secrets \\"
        echo "    --from-literal=line-channel-secret=xxx \\"
        echo "    --from-literal=line-channel-token=xxx \\"
        echo "    --from-literal=openai-api-key=xxx \\"
        echo "    --from-literal=postgres-password=xxx \\"
        echo "    --from-literal=redis-password=xxx \\"
        echo "    --namespace=$NAMESPACE"
        exit 1
    fi
    log_success "Secrets configured"
}

# Deploy databases
deploy_databases() {
    log_info "Deploying databases..."
    
    kubectl apply -f k8s/01-postgres.yaml -n $NAMESPACE
    kubectl apply -f k8s/02-redis.yaml -n $NAMESPACE
    
    log_info "Waiting for databases to be ready..."
    kubectl rollout status statefulset/postgres -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/redis -n $NAMESPACE --timeout=300s
    
    log_success "Databases deployed"
}

# Deploy applications
deploy_applications() {
    log_info "Deploying applications..."
    
    # Update image versions
    if [ "$VERSION" != "latest" ]; then
        log_info "Updating image version to $VERSION..."
        sed -i.bak "s|:latest|:$VERSION|g" k8s/*.yaml
    fi
    
    # Apply configurations
    kubectl apply -f k8s/10-configmap.yaml -n $NAMESPACE
    kubectl apply -f k8s/20-orchestrator.yaml -n $NAMESPACE
    kubectl apply -f k8s/21-analytics.yaml -n $NAMESPACE
    kubectl apply -f k8s/22-nudge.yaml -n $NAMESPACE
    kubectl apply -f k8s/23-trends.yaml -n $NAMESPACE
    kubectl apply -f k8s/30-gateway.yaml -n $NAMESPACE
    
    log_info "Waiting for applications to be ready..."
    kubectl rollout status deployment/orchestrator -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/analytics -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/gateway -n $NAMESPACE --timeout=300s
    
    log_success "Applications deployed"
}

# Deploy ingress
deploy_ingress() {
    log_info "Deploying ingress..."
    
    # Check if ingress controller exists
    if ! kubectl get pods -n ingress-nginx 2>/dev/null | grep -q "ingress-nginx"; then
        log_warn "NGINX Ingress Controller not found. Installing..."
        kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
        log_info "Waiting for ingress controller..."
        kubectl wait --namespace ingress-nginx \
          --for=condition=ready pod \
          --selector=app.kubernetes.io/component=controller \
          --timeout=300s
    fi
    
    # Apply ingress
    kubectl apply -f k8s/40-ingress.yaml -n $NAMESPACE
    
    log_success "Ingress deployed"
}

# Deploy monitoring
deploy_monitoring() {
    log_info "Deploying monitoring stack..."
    
    kubectl apply -f monitoring/namespace.yaml
    kubectl apply -f monitoring/prometheus/ -n monitoring
    kubectl apply -f monitoring/grafana/ -n monitoring
    
    log_info "Waiting for monitoring to be ready..."
    kubectl rollout status deployment/prometheus -n monitoring --timeout=300s
    kubectl rollout status deployment/grafana -n monitoring --timeout=300s
    
    log_success "Monitoring deployed"
}

# Health checks
run_health_checks() {
    log_info "Running health checks..."
    
    # Get gateway endpoint
    GATEWAY_URL=$(kubectl get svc gateway -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    
    if [ -z "$GATEWAY_URL" ]; then
        GATEWAY_URL="localhost:8000"
        log_warn "Using localhost for health checks (port-forward)"
    fi
    
    # Health check
    if curl -sf http://${GATEWAY_URL}/health > /dev/null 2>&1; then
        log_success "Gateway health check passed"
    else
        log_error "Gateway health check failed"
        return 1
    fi
    
    log_success "All health checks passed"
}

# Print deployment summary
print_summary() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              🎉 Deployment Complete! 🎉                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    log_info "Services deployed:"
    kubectl get pods -n $NAMESPACE
    echo ""
    log_info "Ingress:"
    kubectl get ingress -n $NAMESPACE
    echo ""
    log_info "URLs:"
    echo "  Webhook: https://$DOMAIN/webhook"
    echo "  Health:  https://$DOMAIN/health"
    echo "  Dashboard: https://$DOMAIN/dashboard"
    echo ""
    log_info "Commands:"
    echo "  View logs:  kubectl logs -f deployment/gateway -n $NAMESPACE"
    echo "  Scale:      kubectl scale deployment gateway --replicas=3 -n $NAMESPACE"
    echo "  Status:     kubectl get pods -n $NAMESPACE"
    echo ""
    log_info "Monitoring:"
    echo "  kubectl port-forward svc/grafana 3000:3000 -n monitoring"
    echo "  Open: http://localhost:3000 (admin/admin)"
    echo ""
}

# Rollback function
rollback() {
    log_warn "Rolling back deployment..."
    kubectl rollout undo deployment/gateway -n $NAMESPACE
    kubectl rollout undo deployment/orchestrator -n $NAMESPACE
    kubectl rollout undo deployment/analytics -n $NAMESPACE
    log_success "Rollback completed"
}

# Main
trap 'log_error "Deployment failed!"; rollback' ERR

main() {
    print_banner
    check_prerequisites
    
    case ${2:-all} in
        databases)
            deploy_databases
            ;;
        apps)
            deploy_applications
            ;;
        ingress)
            deploy_ingress
            ;;
        monitoring)
            deploy_monitoring
            ;;
        all)
            deploy_databases
            deploy_applications
            deploy_ingress
            deploy_monitoring
            run_health_checks
            print_summary
            ;;
        *)
            echo "Usage: $0 [environment] [component]"
            echo "  environment: production, staging"
            echo "  component: all, databases, apps, ingress, monitoring"
            exit 1
            ;;
    esac
}

main "$@"
