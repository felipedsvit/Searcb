#!/bin/bash

# Script para parar o backend SEARCB
# Autor: Sistema SEARCB
# Data: 2024-01-15

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções utilitárias
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo "🛑 Parando Backend SEARCB..."

# Parar API
if [ -f ".api.pid" ]; then
    API_PID=$(cat .api.pid)
    if kill -0 $API_PID 2>/dev/null; then
        print_info "Parando API (PID: $API_PID)..."
        kill $API_PID
        rm .api.pid
        print_success "API parada"
    else
        print_warning "API não estava funcionando"
        rm -f .api.pid
    fi
else
    print_warning "API não iniciada"
fi

# Parar Celery Worker
if [ -f ".worker.pid" ]; then
    WORKER_PID=$(cat .worker.pid)
    if kill -0 $WORKER_PID 2>/dev/null; then
        print_info "Parando Celery Worker (PID: $WORKER_PID)..."
        kill $WORKER_PID
        rm .worker.pid
        print_success "Celery Worker parado"
    else
        print_warning "Celery Worker não estava funcionando"
        rm -f .worker.pid
    fi
else
    print_warning "Celery Worker não iniciado"
fi

# Parar Celery Beat
if [ -f ".beat.pid" ]; then
    BEAT_PID=$(cat .beat.pid)
    if kill -0 $BEAT_PID 2>/dev/null; then
        print_info "Parando Celery Beat (PID: $BEAT_PID)..."
        kill $BEAT_PID
        rm .beat.pid
        print_success "Celery Beat parado"
    else
        print_warning "Celery Beat não estava funcionando"
        rm -f .beat.pid
    fi
else
    print_warning "Celery Beat não iniciado"
fi

# Verificar se ainda há processos rodando
print_info "Verificando processos restantes..."

# Matar processos remanescentes do uvicorn
pkill -f "uvicorn app.main:app" 2>/dev/null || true

# Matar processos remanescentes do celery
pkill -f "celery.*app.tasks.sync_tasks" 2>/dev/null || true

print_success "Backend SEARCB parado com sucesso!"
print_info "Logs preservados em: logs/"
