#!/bin/bash

# Script para inicializar o backend SEARCB
# Autor: Sistema SEARCB
# Data: 2024-01-15

set -e

echo "🚀 Iniciando Backend SEARCB..."

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

# Verificar se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt não encontrado. Execute este script no diretório do backend."
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não está instalado."
    exit 1
fi

print_info "Python $(python3 --version) encontrado"

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    print_info "Criando ambiente virtual..."
    python3 -m venv venv
    print_success "Ambiente virtual criado"
fi

# Ativar ambiente virtual
print_info "Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
print_info "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Dependências instaladas"

# Verificar variáveis de ambiente
print_info "Verificando variáveis de ambiente..."

if [ ! -f ".env" ]; then
    print_warning ".env não encontrado. Criando arquivo exemplo..."
    cat > .env << EOF
# Configuração do Banco de Dados
DATABASE_URL=postgresql://user:password@localhost:5432/searcb
DATABASE_TEST_URL=postgresql://user:password@localhost:5432/searcb_test

# Configuração do Redis
REDIS_URL=redis://localhost:6379/0

# Configuração de Segurança
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Configuração da API PNCP
PNCP_API_URL=https://pncp.gov.br/api/v1
PNCP_API_KEY=your-pncp-api-key-here

# Configuração CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
CORS_CREDENTIALS=true
CORS_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_HEADERS=["*"]

# Configuração de Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Configuração do Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Configuração de Logging
LOG_LEVEL=INFO
LOG_FILE=logs/searcb.log

# Configuração de Uploads
UPLOAD_DIR=uploads/
MAX_UPLOAD_SIZE=10485760

# Configuração do Ambiente
ENVIRONMENT=development
DEBUG=true
EOF
    print_warning "Arquivo .env criado. Configure as variáveis antes de prosseguir."
fi

# Verificar PostgreSQL
print_info "Verificando PostgreSQL..."
if command -v psql &> /dev/null; then
    print_success "PostgreSQL encontrado"
else
    print_warning "PostgreSQL não encontrado. Instale antes de prosseguir."
fi

# Verificar Redis
print_info "Verificando Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        print_success "Redis está funcionando"
    else
        print_warning "Redis não está respondendo. Inicie o serviço Redis."
    fi
else
    print_warning "Redis não encontrado. Instale antes de prosseguir."
fi

# Criar diretórios necessários
print_info "Criando diretórios..."
mkdir -p logs
mkdir -p uploads
mkdir -p backups
mkdir -p temp
print_success "Diretórios criados"

# Configurar banco de dados
print_info "Configurando banco de dados..."
if python -c "from app.core.database import engine; engine.connect()" 2>/dev/null; then
    print_success "Conexão com banco de dados estabelecida"
    
    # Executar migrações
    print_info "Executando migrações..."
    alembic upgrade head
    print_success "Migrações executadas"
else
    print_warning "Não foi possível conectar ao banco de dados. Verifique as configurações."
fi

# Executar testes
print_info "Executando testes..."
if python -m pytest tests/ -v --tb=short; then
    print_success "Todos os testes passaram"
else
    print_warning "Alguns testes falharam. Verifique os logs."
fi

# Função para iniciar serviços
start_services() {
    echo
    print_info "Iniciando serviços..."
    
    # Iniciar API
    print_info "Iniciando API na porta 8000..."
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > logs/api.log 2>&1 &
    API_PID=$!
    echo $API_PID > .api.pid
    
    # Aguardar API iniciar
    sleep 5
    
    # Verificar se API está funcionando
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "API iniciada com sucesso (PID: $API_PID)"
        print_info "API disponível em: http://localhost:8000"
        print_info "Documentação em: http://localhost:8000/docs"
    else
        print_error "Erro ao iniciar API"
        return 1
    fi
    
    # Iniciar Celery Worker
    print_info "Iniciando Celery Worker..."
    nohup celery -A app.tasks.sync_tasks worker --loglevel=info > logs/celery_worker.log 2>&1 &
    WORKER_PID=$!
    echo $WORKER_PID > .worker.pid
    print_success "Celery Worker iniciado (PID: $WORKER_PID)"
    
    # Iniciar Celery Beat
    print_info "Iniciando Celery Beat..."
    nohup celery -A app.tasks.sync_tasks beat --loglevel=info > logs/celery_beat.log 2>&1 &
    BEAT_PID=$!
    echo $BEAT_PID > .beat.pid
    print_success "Celery Beat iniciado (PID: $BEAT_PID)"
    
    echo
    print_success "Todos os serviços iniciados com sucesso!"
    print_info "Logs disponíveis em: logs/"
    print_info "Para parar os serviços, execute: ./stop.sh"
}

# Função para parar serviços
stop_services() {
    echo
    print_info "Parando serviços..."
    
    # Parar API
    if [ -f ".api.pid" ]; then
        API_PID=$(cat .api.pid)
        if kill -0 $API_PID 2>/dev/null; then
            kill $API_PID
            rm .api.pid
            print_success "API parada"
        fi
    fi
    
    # Parar Celery Worker
    if [ -f ".worker.pid" ]; then
        WORKER_PID=$(cat .worker.pid)
        if kill -0 $WORKER_PID 2>/dev/null; then
            kill $WORKER_PID
            rm .worker.pid
            print_success "Celery Worker parado"
        fi
    fi
    
    # Parar Celery Beat
    if [ -f ".beat.pid" ]; then
        BEAT_PID=$(cat .beat.pid)
        if kill -0 $BEAT_PID 2>/dev/null; then
            kill $BEAT_PID
            rm .beat.pid
            print_success "Celery Beat parado"
        fi
    fi
    
    print_success "Todos os serviços foram parados"
}

# Função para status dos serviços
status_services() {
    echo
    print_info "Status dos serviços:"
    
    # Status API
    if [ -f ".api.pid" ]; then
        API_PID=$(cat .api.pid)
        if kill -0 $API_PID 2>/dev/null; then
            print_success "API: Funcionando (PID: $API_PID)"
        else
            print_error "API: Não está funcionando"
        fi
    else
        print_error "API: Não iniciada"
    fi
    
    # Status Celery Worker
    if [ -f ".worker.pid" ]; then
        WORKER_PID=$(cat .worker.pid)
        if kill -0 $WORKER_PID 2>/dev/null; then
            print_success "Celery Worker: Funcionando (PID: $WORKER_PID)"
        else
            print_error "Celery Worker: Não está funcionando"
        fi
    else
        print_error "Celery Worker: Não iniciado"
    fi
    
    # Status Celery Beat
    if [ -f ".beat.pid" ]; then
        BEAT_PID=$(cat .beat.pid)
        if kill -0 $BEAT_PID 2>/dev/null; then
            print_success "Celery Beat: Funcionando (PID: $BEAT_PID)"
        else
            print_error "Celery Beat: Não está funcionando"
        fi
    else
        print_error "Celery Beat: Não iniciado"
    fi
}

# Menu principal
case "${1:-}" in
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 2
        start_services
        ;;
    "status")
        status_services
        ;;
    "install")
        print_success "Instalação concluída!"
        ;;
    *)
        echo
        print_info "Backend SEARCB configurado com sucesso!"
        echo
        echo "Comandos disponíveis:"
        echo "  ./start.sh start    - Iniciar todos os serviços"
        echo "  ./start.sh stop     - Parar todos os serviços"
        echo "  ./start.sh restart  - Reiniciar todos os serviços"
        echo "  ./start.sh status   - Status dos serviços"
        echo
        echo "URLs importantes:"
        echo "  API: http://localhost:8000"
        echo "  Documentação: http://localhost:8000/docs"
        echo "  Admin: http://localhost:8000/admin"
        echo
        print_warning "Não esqueça de configurar o arquivo .env antes de iniciar os serviços!"
        ;;
esac
