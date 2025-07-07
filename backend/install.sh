#!/bin/bash

# Script de instalação e configuração do Sistema PNCP Backend
# Author: Sistema PNCP Team
# Version: 1.0.0

set -e

echo "🚀 Iniciando instalação do Sistema PNCP Backend..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python 3.8+ is installed
check_python() {
    echo -e "${BLUE}Verificando Python...${NC}"
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo -e "${GREEN}Python ${PYTHON_VERSION} encontrado${NC}"
        
        # Check if version is 3.8+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            echo -e "${GREEN}Versão do Python é compatível${NC}"
        else
            echo -e "${RED}Python 3.8+ é necessário. Versão atual: ${PYTHON_VERSION}${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Python 3 não encontrado. Instale Python 3.8+ antes de continuar.${NC}"
        exit 1
    fi
}

# Check if PostgreSQL is running
check_postgresql() {
    echo -e "${BLUE}Verificando PostgreSQL...${NC}"
    if command -v psql &> /dev/null; then
        echo -e "${GREEN}PostgreSQL encontrado${NC}"
        
        # Check if PostgreSQL service is running
        if pg_isready -q; then
            echo -e "${GREEN}PostgreSQL está rodando${NC}"
        else
            echo -e "${YELLOW}PostgreSQL não está rodando. Tente iniciar o serviço:${NC}"
            echo -e "${YELLOW}sudo systemctl start postgresql${NC}"
        fi
    else
        echo -e "${YELLOW}PostgreSQL não encontrado. Instale PostgreSQL antes de continuar.${NC}"
        echo -e "${YELLOW}Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib${NC}"
        echo -e "${YELLOW}CentOS/RHEL: sudo yum install postgresql-server postgresql-contrib${NC}"
    fi
}

# Check if Redis is running
check_redis() {
    echo -e "${BLUE}Verificando Redis...${NC}"
    if command -v redis-cli &> /dev/null; then
        echo -e "${GREEN}Redis encontrado${NC}"
        
        # Check if Redis service is running
        if redis-cli ping > /dev/null 2>&1; then
            echo -e "${GREEN}Redis está rodando${NC}"
        else
            echo -e "${YELLOW}Redis não está rodando. Tente iniciar o serviço:${NC}"
            echo -e "${YELLOW}sudo systemctl start redis${NC}"
        fi
    else
        echo -e "${YELLOW}Redis não encontrado. Instale Redis antes de continuar.${NC}"
        echo -e "${YELLOW}Ubuntu/Debian: sudo apt-get install redis-server${NC}"
        echo -e "${YELLOW}CentOS/RHEL: sudo yum install redis${NC}"
    fi
}

# Create virtual environment
create_venv() {
    echo -e "${BLUE}Criando ambiente virtual...${NC}"
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}Ambiente virtual criado${NC}"
    else
        echo -e "${YELLOW}Ambiente virtual já existe${NC}"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    echo -e "${GREEN}Ambiente virtual ativado${NC}"
    
    # Upgrade pip
    pip install --upgrade pip
}

# Install Python dependencies
install_dependencies() {
    echo -e "${BLUE}Instalando dependências Python...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}Dependências instaladas com sucesso${NC}"
}

# Create .env file if it doesn't exist
create_env_file() {
    echo -e "${BLUE}Configurando arquivo .env...${NC}"
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://pncp_user:pncp_password@localhost:5432/pncp_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Security Configuration
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# PNCP Configuration
PNCP_WEBHOOK_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
EOF
        echo -e "${GREEN}Arquivo .env criado${NC}"
    else
        echo -e "${YELLOW}Arquivo .env já existe${NC}"
    fi
}

# Setup database
setup_database() {
    echo -e "${BLUE}Configurando banco de dados...${NC}"
    
    # Create database and user
    echo -e "${YELLOW}Execute os seguintes comandos no PostgreSQL para criar o banco:${NC}"
    echo -e "${YELLOW}sudo -u postgres psql${NC}"
    echo -e "${YELLOW}CREATE DATABASE pncp_db;${NC}"
    echo -e "${YELLOW}CREATE USER pncp_user WITH ENCRYPTED PASSWORD 'pncp_password';${NC}"
    echo -e "${YELLOW}GRANT ALL PRIVILEGES ON DATABASE pncp_db TO pncp_user;${NC}"
    echo -e "${YELLOW}\\q${NC}"
    
    read -p "Pressione Enter após configurar o banco de dados..."
    
    # Run migrations
    echo -e "${BLUE}Executando migrações...${NC}"
    alembic upgrade head
    echo -e "${GREEN}Migrações executadas com sucesso${NC}"
}

# Create initial admin user
create_admin_user() {
    echo -e "${BLUE}Criando usuário administrador...${NC}"
    
    python3 -c "
from app.core.database import SessionLocal, init_db
from app.core.security import security_service
from app.models.usuario import Usuario
from datetime import datetime

init_db()
db = SessionLocal()

# Check if admin user already exists
admin_user = db.query(Usuario).filter(Usuario.username == 'admin').first()

if not admin_user:
    admin_user = Usuario(
        username='admin',
        email='admin@sistema-pncp.gov.br',
        nome_completo='Administrador do Sistema',
        senha_hash=security_service.get_password_hash('admin123'),
        ativo=True,
        is_admin=True,
        is_gestor=True,
        is_operador=True,
        cargo='Administrador',
        departamento='TI'
    )
    db.add(admin_user)
    db.commit()
    print('Usuário admin criado com sucesso')
    print('Username: admin')
    print('Password: admin123')
    print('IMPORTANTE: Altere a senha padrão após o primeiro login!')
else:
    print('Usuário admin já existe')

db.close()
"
    echo -e "${GREEN}Usuário administrador configurado${NC}"
}

# Create systemd service files
create_systemd_services() {
    echo -e "${BLUE}Criando serviços systemd...${NC}"
    
    # Get current directory
    CURRENT_DIR=$(pwd)
    
    # Create FastAPI service
    sudo tee /etc/systemd/system/pncp-api.service > /dev/null << EOF
[Unit]
Description=Sistema PNCP API
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Create Celery worker service
    sudo tee /etc/systemd/system/pncp-worker.service > /dev/null << EOF
[Unit]
Description=Sistema PNCP Celery Worker
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/celery -A app.tasks worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Create Celery beat service
    sudo tee /etc/systemd/system/pncp-beat.service > /dev/null << EOF
[Unit]
Description=Sistema PNCP Celery Beat
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/celery -A app.tasks beat --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    sudo systemctl daemon-reload
    
    echo -e "${GREEN}Serviços systemd criados${NC}"
    echo -e "${YELLOW}Para iniciar os serviços:${NC}"
    echo -e "${YELLOW}sudo systemctl enable pncp-api pncp-worker pncp-beat${NC}"
    echo -e "${YELLOW}sudo systemctl start pncp-api pncp-worker pncp-beat${NC}"
}

# Create nginx configuration
create_nginx_config() {
    echo -e "${BLUE}Criando configuração do Nginx...${NC}"
    
    sudo tee /etc/nginx/sites-available/pncp-api << EOF
server {
    listen 80;
    server_name sistema-pncp.local;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /static/ {
        alias /var/www/pncp-static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
EOF

    # Enable site
    sudo ln -sf /etc/nginx/sites-available/pncp-api /etc/nginx/sites-enabled/
    
    # Test nginx configuration
    sudo nginx -t
    
    echo -e "${GREEN}Configuração do Nginx criada${NC}"
    echo -e "${YELLOW}Para aplicar as mudanças:${NC}"
    echo -e "${YELLOW}sudo systemctl reload nginx${NC}"
}

# Main installation function
main() {
    echo -e "${GREEN}=== Sistema PNCP Backend - Instalação ===${NC}"
    echo ""
    
    check_python
    check_postgresql
    check_redis
    
    create_venv
    install_dependencies
    create_env_file
    
    echo ""
    echo -e "${YELLOW}Configure o banco de dados PostgreSQL antes de continuar.${NC}"
    read -p "Deseja continuar com a configuração do banco? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_database
        create_admin_user
    fi
    
    echo ""
    read -p "Deseja criar os serviços systemd? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_systemd_services
    fi
    
    echo ""
    read -p "Deseja criar a configuração do Nginx? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_nginx_config
    fi
    
    echo ""
    echo -e "${GREEN}=== Instalação Concluída ===${NC}"
    echo ""
    echo -e "${BLUE}Para iniciar o servidor de desenvolvimento:${NC}"
    echo -e "${YELLOW}source venv/bin/activate${NC}"
    echo -e "${YELLOW}uvicorn app.main:app --reload --host 0.0.0.0 --port 8000${NC}"
    echo ""
    echo -e "${BLUE}Para iniciar o worker Celery:${NC}"
    echo -e "${YELLOW}source venv/bin/activate${NC}"
    echo -e "${YELLOW}celery -A app.tasks worker --loglevel=info${NC}"
    echo ""
    echo -e "${BLUE}Para iniciar o Celery Beat:${NC}"
    echo -e "${YELLOW}source venv/bin/activate${NC}"
    echo -e "${YELLOW}celery -A app.tasks beat --loglevel=info${NC}"
    echo ""
    echo -e "${BLUE}Documentação da API estará disponível em:${NC}"
    echo -e "${YELLOW}http://localhost:8000/api/v1/docs${NC}"
    echo ""
    echo -e "${BLUE}Credenciais do administrador:${NC}"
    echo -e "${YELLOW}Username: admin${NC}"
    echo -e "${YELLOW}Password: admin123${NC}"
    echo -e "${RED}IMPORTANTE: Altere a senha padrão após o primeiro login!${NC}"
}

# Run main function
main "$@"
