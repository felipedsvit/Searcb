# Guia de Deploy - SEARCB Backend

## Visão Geral

Este guia fornece instruções completas para fazer deploy do backend SEARCB em diferentes ambientes (desenvolvimento, homologação e produção).

## Pré-requisitos

### Infraestrutura Necessária

- **Servidor**: Ubuntu 20.04+ ou CentOS 8+
- **CPU**: Mínimo 2 cores (recomendado 4 cores para produção)
- **RAM**: Mínimo 4GB (recomendado 8GB para produção)
- **Disco**: Mínimo 50GB SSD
- **Network**: Conexão estável com internet

### Software Necessário

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Nginx 1.18+
- SSL Certificate (Let's Encrypt recomendado)
- Docker (opcional)

## Configuração do Servidor

### 1. Atualização do Sistema

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. Instalação de Dependências

```bash
# Ubuntu/Debian
sudo apt install -y python3.11 python3.11-venv python3.11-dev \
    postgresql postgresql-contrib redis-server nginx \
    git curl wget unzip supervisor

# CentOS/RHEL
sudo yum install -y python3.11 python3.11-venv python3.11-devel \
    postgresql postgresql-server postgresql-contrib redis nginx \
    git curl wget unzip supervisor
```

### 3. Configuração do PostgreSQL

```bash
# Inicializar banco (CentOS apenas)
sudo postgresql-setup initdb

# Iniciar serviços
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar usuário e banco
sudo -u postgres psql << EOF
CREATE USER searcb WITH PASSWORD 'senha_segura_aqui';
CREATE DATABASE searcb_db OWNER searcb;
GRANT ALL PRIVILEGES ON DATABASE searcb_db TO searcb;
\q
EOF
```

### 4. Configuração do Redis

```bash
# Iniciar Redis
sudo systemctl start redis
sudo systemctl enable redis

# Configurar Redis (opcional)
sudo nano /etc/redis/redis.conf
# Configurar:
# maxmemory 1gb
# maxmemory-policy allkeys-lru
# save 900 1
# save 300 10
# save 60 10000

sudo systemctl restart redis
```

## Deploy da Aplicação

### 1. Preparação do Ambiente

```bash
# Criar usuário para aplicação
sudo useradd -m -s /bin/bash searcb
sudo usermod -aG sudo searcb

# Mudar para usuário searcb
sudo su - searcb

# Criar diretórios
mkdir -p /home/searcb/app
mkdir -p /home/searcb/logs
mkdir -p /home/searcb/backups
```

### 2. Clone e Configuração do Código

```bash
# Clone do repositório
cd /home/searcb
git clone https://github.com/your-org/searcb.git
cd searcb/backend

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuração das Variáveis de Ambiente

```bash
# Criar arquivo de configuração
cat > /home/searcb/searcb/backend/.env << EOF
# Environment
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://searcb:senha_segura_aqui@localhost/searcb_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
SECRET_KEY=$(openssl rand -base64 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# PNCP
PNCP_API_URL=https://api.gov.br/pncp/v1
PNCP_TOKEN=seu_token_pncp_aqui

# Logs
LOG_LEVEL=INFO
LOG_FILE=/home/searcb/logs/app.log

# Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=searcb@yourdomain.com
SMTP_PASSWORD=sua_senha_app_gmail

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
EOF

# Proteger arquivo de configuração
chmod 600 /home/searcb/searcb/backend/.env
```

### 4. Migrações do Banco de Dados

```bash
cd /home/searcb/searcb/backend
source venv/bin/activate

# Executar migrações
alembic upgrade head

# Criar usuário admin inicial
python -c "
from app.core.database import SessionLocal
from app.services.usuario_service import UsuarioService
from app.schemas.usuario import UsuarioCreate

db = SessionLocal()
usuario_service = UsuarioService(db)

admin_data = UsuarioCreate(
    username='admin',
    email='admin@searcb.gov.br',
    nome_completo='Administrador do Sistema',
    senha='SenhaSeguraAdmin123!',
    confirmar_senha='SenhaSeguraAdmin123!',
    is_admin=True
)

import asyncio
asyncio.run(usuario_service.create_usuario(admin_data))
db.close()
print('Usuário admin criado com sucesso!')
"
```

## Configuração de Serviços

### 1. Configuração do Gunicorn

```bash
# Criar arquivo de configuração do Gunicorn
cat > /home/searcb/searcb/backend/gunicorn.conf.py << EOF
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "searcb"
group = "searcb"
pythonpath = "/home/searcb/searcb/backend"
chdir = "/home/searcb/searcb/backend"

# Logging
accesslog = "/home/searcb/logs/access.log"
errorlog = "/home/searcb/logs/error.log"
loglevel = "info"
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
EOF
```

### 2. Configuração do Supervisor

```bash
# Configuração do serviço principal
sudo tee /etc/supervisor/conf.d/searcb-app.conf << EOF
[program:searcb-app]
command=/home/searcb/searcb/backend/venv/bin/gunicorn app.main:app -c gunicorn.conf.py
directory=/home/searcb/searcb/backend
user=searcb
group=searcb
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/searcb/logs/app.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
environment=PATH="/home/searcb/searcb/backend/venv/bin"
EOF

# Configuração do Celery Worker
sudo tee /etc/supervisor/conf.d/searcb-celery.conf << EOF
[program:searcb-celery]
command=/home/searcb/searcb/backend/venv/bin/celery -A app.tasks.sync_tasks worker --loglevel=info --concurrency=4
directory=/home/searcb/searcb/backend
user=searcb
group=searcb
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/searcb/logs/celery.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
environment=PATH="/home/searcb/searcb/backend/venv/bin"
EOF

# Configuração do Celery Beat
sudo tee /etc/supervisor/conf.d/searcb-beat.conf << EOF
[program:searcb-beat]
command=/home/searcb/searcb/backend/venv/bin/celery -A app.tasks.sync_tasks beat --loglevel=info
directory=/home/searcb/searcb/backend
user=searcb
group=searcb
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/searcb/logs/beat.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
environment=PATH="/home/searcb/searcb/backend/venv/bin"
EOF

# Recarregar supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### 3. Configuração do Nginx

```bash
# Criar configuração do site
sudo tee /etc/nginx/sites-available/searcb << EOF
upstream searcb_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name searcb.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name searcb.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/searcb.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/searcb.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;
    
    # Main location
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://searcb_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        proxy_buffering on;
        proxy_buffer_size 8k;
        proxy_buffers 8 8k;
        proxy_busy_buffers_size 16k;
    }
    
    # Authentication endpoints with stricter rate limiting
    location /auth/login {
        limit_req zone=login burst=5 nodelay;
        
        proxy_pass http://searcb_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://searcb_backend;
        proxy_set_header Host \$host;
    }
    
    # Static files (if any)
    location /static/ {
        alias /home/searcb/searcb/backend/static/;
        expires 1M;
        add_header Cache-Control "public, immutable";
    }
    
    # Logs
    access_log /var/log/nginx/searcb_access.log;
    error_log /var/log/nginx/searcb_error.log;
}
EOF

# Habilitar site
sudo ln -s /etc/nginx/sites-available/searcb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Configuração de SSL

### 1. Instalação do Certbot

```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

### 2. Obtenção do Certificado SSL

```bash
# Obter certificado
sudo certbot --nginx -d searcb.yourdomain.com

# Configurar renovação automática
sudo crontab -e
# Adicionar linha:
0 12 * * * /usr/bin/certbot renew --quiet
```

## Configuração de Monitoramento

### 1. Configuração de Logs

```bash
# Configurar logrotate
sudo tee /etc/logrotate.d/searcb << EOF
/home/searcb/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 searcb searcb
    postrotate
        sudo supervisorctl restart searcb-app
    endscript
}
EOF
```

### 2. Configuração de Backup

```bash
# Criar script de backup
cat > /home/searcb/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/searcb/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="searcb_db"
DB_USER="searcb"

# Backup do banco de dados
pg_dump -h localhost -U $DB_USER -d $DB_NAME > "$BACKUP_DIR/db_backup_$DATE.sql"

# Backup dos arquivos de configuração
tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" /home/searcb/searcb/backend/.env

# Remover backups antigos (manter 7 dias)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /home/searcb/backup.sh

# Configurar cron para backup diário
crontab -e
# Adicionar linha:
0 2 * * * /home/searcb/backup.sh
```

## Configuração de Firewall

```bash
# Ubuntu/Debian (UFW)
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from 127.0.0.1 to any port 5432
sudo ufw allow from 127.0.0.1 to any port 6379

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

## Verificação e Testes

### 1. Verificação de Serviços

```bash
# Verificar status dos serviços
sudo systemctl status postgresql
sudo systemctl status redis
sudo systemctl status nginx
sudo supervisorctl status

# Verificar logs
sudo tail -f /home/searcb/logs/app.log
sudo tail -f /home/searcb/logs/celery.log
sudo tail -f /var/log/nginx/searcb_access.log
```

### 2. Testes de Conectividade

```bash
# Teste de health check
curl -k https://searcb.yourdomain.com/health

# Teste de autenticação
curl -k -X POST https://searcb.yourdomain.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "SenhaSeguraAdmin123!"}'

# Teste de endpoint protegido
curl -k -H "Authorization: Bearer <token>" \
  https://searcb.yourdomain.com/usuarios/me/profile
```

## Manutenção

### 1. Comandos Úteis

```bash
# Restart dos serviços
sudo supervisorctl restart searcb-app
sudo supervisorctl restart searcb-celery
sudo supervisorctl restart searcb-beat

# Verificar logs em tempo real
sudo tail -f /home/searcb/logs/app.log

# Verificar status das tarefas Celery
cd /home/searcb/searcb/backend
source venv/bin/activate
celery -A app.tasks.sync_tasks inspect active

# Executar migração manual
alembic upgrade head
```

### 2. Atualização da Aplicação

```bash
# Parar serviços
sudo supervisorctl stop searcb-app
sudo supervisorctl stop searcb-celery
sudo supervisorctl stop searcb-beat

# Atualizar código
cd /home/searcb/searcb
git pull origin main

# Atualizar dependências
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Executar migrações
alembic upgrade head

# Reiniciar serviços
sudo supervisorctl start searcb-app
sudo supervisorctl start searcb-celery
sudo supervisorctl start searcb-beat
```

## Troubleshooting

### 1. Problemas Comuns

#### Aplicação não inicia
```bash
# Verificar logs
sudo tail -f /home/searcb/logs/app.log

# Verificar configurações
source /home/searcb/searcb/backend/venv/bin/activate
cd /home/searcb/searcb/backend
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

#### Banco de dados não conecta
```bash
# Verificar status do PostgreSQL
sudo systemctl status postgresql

# Testar conexão
psql -h localhost -U searcb -d searcb_db
```

#### Redis não conecta
```bash
# Verificar status do Redis
sudo systemctl status redis

# Testar conexão
redis-cli ping
```

#### Nginx não funciona
```bash
# Verificar configuração
sudo nginx -t

# Verificar logs
sudo tail -f /var/log/nginx/error.log
```

### 2. Monitoramento de Performance

```bash
# Monitorar CPU e memória
top
htop

# Monitorar conexões de rede
netstat -tlnp | grep :8000
ss -tlnp | grep :8000

# Monitorar banco de dados
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

## Segurança

### 1. Checklist de Segurança

- [ ] Senhas fortes configuradas
- [ ] Firewall configurado
- [ ] SSL/TLS habilitado
- [ ] Headers de segurança configurados
- [ ] Rate limiting ativo
- [ ] Logs de auditoria habilitados
- [ ] Backups automáticos configurados
- [ ] Atualizações de segurança aplicadas

### 2. Hardening Adicional

```bash
# Desabilitar root login via SSH
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Configurar fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Configurar auditoria
sudo apt install auditd
sudo systemctl enable auditd
sudo systemctl start auditd
```

## Contato

Para dúvidas sobre deploy:
- **Email**: devops@searcb.gov.br
- **Documentação**: https://docs.searcb.gov.br/deploy
- **Suporte**: https://support.searcb.gov.br
