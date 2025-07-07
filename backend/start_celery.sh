#!/bin/bash

# Script para iniciar workers Celery

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Iniciando Workers Celery SEARCB ===${NC}"

# Verificar se o Redis está rodando
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}Erro: Redis não está rodando. Inicie o Redis primeiro.${NC}"
    exit 1
fi

# Verificar se o PostgreSQL está rodando
if ! pg_isready -q; then
    echo -e "${RED}Erro: PostgreSQL não está rodando. Inicie o PostgreSQL primeiro.${NC}"
    exit 1
fi

# Diretório do projeto
PROJECT_DIR="$(dirname "$(readlink -f "$0")")"
cd "$PROJECT_DIR"

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo -e "${YELLOW}Ativando ambiente virtual...${NC}"
    source venv/bin/activate
fi

# Função para iniciar worker
start_worker() {
    local queue=$1
    local concurrency=${2:-2}
    local log_level=${3:-info}
    
    echo -e "${GREEN}Iniciando worker para fila: ${queue}${NC}"
    
    celery -A app.tasks.sync_tasks worker \
        --loglevel=$log_level \
        --concurrency=$concurrency \
        --queues=$queue \
        --hostname=worker-$queue@%h \
        --pidfile=/tmp/celery-$queue.pid \
        --logfile=logs/celery-$queue.log \
        --detach
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Worker $queue iniciado com sucesso${NC}"
    else
        echo -e "${RED}Erro ao iniciar worker $queue${NC}"
        return 1
    fi
}

# Função para iniciar beat scheduler
start_beat() {
    echo -e "${GREEN}Iniciando Celery Beat Scheduler...${NC}"
    
    celery -A app.tasks.sync_tasks beat \
        --loglevel=info \
        --pidfile=/tmp/celery-beat.pid \
        --logfile=logs/celery-beat.log \
        --detach
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Celery Beat iniciado com sucesso${NC}"
    else
        echo -e "${RED}Erro ao iniciar Celery Beat${NC}"
        return 1
    fi
}

# Criar diretório de logs se não existir
mkdir -p logs

# Iniciar workers para diferentes filas
echo -e "${YELLOW}Iniciando workers especializados...${NC}"

# Worker para sincronização (CPU intensivo)
start_worker "sync" 1 "info"

# Worker para manutenção (I/O intensivo)
start_worker "maintenance" 2 "info"

# Worker para backup (I/O intensivo)
start_worker "backup" 1 "info"

# Worker para relatórios (CPU intensivo)
start_worker "reports" 1 "info"

# Worker para monitoramento (baixa latência)
start_worker "monitoring" 4 "warning"

# Worker para validação (CPU intensivo)
start_worker "validation" 1 "info"

# Worker para notificações (alta velocidade)
start_worker "notifications" 3 "info"

# Worker geral para outras tarefas
start_worker "celery" 2 "info"

# Aguardar um pouco para os workers iniciarem
sleep 2

# Iniciar beat scheduler
start_beat

echo -e "${GREEN}=== Todos os workers foram iniciados ===${NC}"
echo -e "${YELLOW}Para monitorar os workers, use:${NC}"
echo -e "  celery -A app.tasks.sync_tasks inspect active"
echo -e "  celery -A app.tasks.sync_tasks inspect stats"
echo -e "  celery -A app.tasks.sync_tasks flower"
echo -e ""
echo -e "${YELLOW}Para parar os workers, use:${NC}"
echo -e "  ./stop_celery.sh"
echo -e ""
echo -e "${YELLOW}Logs dos workers estão em: logs/celery-*.log${NC}"

# Verificar se todos os workers estão rodando
echo -e "${YELLOW}Verificando status dos workers...${NC}"
sleep 3

celery -A app.tasks.sync_tasks inspect ping --timeout=10
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Todos os workers estão respondendo${NC}"
else
    echo -e "${YELLOW}Alguns workers podem não estar respondendo ainda${NC}"
fi

# Mostrar estatísticas iniciais
echo -e "${YELLOW}Estatísticas iniciais:${NC}"
celery -A app.tasks.sync_tasks inspect stats --timeout=5 2>/dev/null || echo "Estatísticas não disponíveis ainda"
