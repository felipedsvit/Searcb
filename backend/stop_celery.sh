#!/bin/bash

# Script para parar workers Celery

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Parando Workers Celery SEARCB ===${NC}"

# Função para parar worker
stop_worker() {
    local queue=$1
    local pidfile="/tmp/celery-$queue.pid"
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}Parando worker $queue (PID: $pid)...${NC}"
            kill -TERM "$pid"
            
            # Aguardar até 10 segundos para o processo terminar
            local count=0
            while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${RED}Worker $queue não terminou, forçando parada...${NC}"
                kill -KILL "$pid"
            fi
            
            rm -f "$pidfile"
            echo -e "${GREEN}Worker $queue parado${NC}"
        else
            echo -e "${YELLOW}Worker $queue não está rodando${NC}"
            rm -f "$pidfile"
        fi
    else
        echo -e "${YELLOW}PID file para worker $queue não encontrado${NC}"
    fi
}

# Função para parar beat scheduler
stop_beat() {
    local pidfile="/tmp/celery-beat.pid"
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}Parando Celery Beat (PID: $pid)...${NC}"
            kill -TERM "$pid"
            
            # Aguardar até 10 segundos para o processo terminar
            local count=0
            while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${RED}Celery Beat não terminou, forçando parada...${NC}"
                kill -KILL "$pid"
            fi
            
            rm -f "$pidfile"
            echo -e "${GREEN}Celery Beat parado${NC}"
        else
            echo -e "${YELLOW}Celery Beat não está rodando${NC}"
            rm -f "$pidfile"
        fi
    else
        echo -e "${YELLOW}PID file para Celery Beat não encontrado${NC}"
    fi
}

# Parar beat scheduler primeiro
stop_beat

# Parar todos os workers
echo -e "${YELLOW}Parando workers especializados...${NC}"

stop_worker "sync"
stop_worker "maintenance"
stop_worker "backup"
stop_worker "reports"
stop_worker "monitoring"
stop_worker "validation"
stop_worker "notifications"
stop_worker "celery"

# Parar qualquer processo celery restante
echo -e "${YELLOW}Verificando processos celery restantes...${NC}"
celery_pids=$(pgrep -f "celery.*worker" || true)
if [ -n "$celery_pids" ]; then
    echo -e "${YELLOW}Parando processos celery restantes...${NC}"
    echo "$celery_pids" | xargs kill -TERM
    sleep 2
    
    # Verificar se ainda há processos
    celery_pids=$(pgrep -f "celery.*worker" || true)
    if [ -n "$celery_pids" ]; then
        echo -e "${RED}Forçando parada de processos celery restantes...${NC}"
        echo "$celery_pids" | xargs kill -KILL
    fi
fi

# Limpar arquivos temporários
echo -e "${YELLOW}Limpando arquivos temporários...${NC}"
rm -f /tmp/celery-*.pid
rm -f celerybeat-schedule

echo -e "${GREEN}=== Todos os workers foram parados ===${NC}"

# Verificar se ainda há processos celery rodando
remaining_pids=$(pgrep -f "celery" || true)
if [ -n "$remaining_pids" ]; then
    echo -e "${YELLOW}Processos celery ainda rodando:${NC}"
    ps aux | grep celery | grep -v grep
else
    echo -e "${GREEN}Nenhum processo celery está rodando${NC}"
fi
