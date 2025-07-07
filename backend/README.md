# Sistema SEARCB - Backend

Sistema de Gestão Pública integrado ao Portal Nacional de Contratações Públicas (PNCP), desenvolvido em Python com FastAPI, conforme a Lei nº 14.133/2021.

## 🚀 Características

- **API RESTful completa** para consulta de dados do PNCP
- **Integração nativa** com as APIs do Portal Nacional de Contratações Públicas
- **Cache inteligente** com Redis para otimização de performance
- **Sincronização automática** de dados com Celery
- **Webhook handler** para notificações em tempo real
- **Autenticação robusta** com JWT
- **Rate limiting** e controle de acesso
- **Monitoramento completo** com logs estruturados
- **Documentação automática** com Swagger/OpenAPI
- **Sistema de logs centralizado** para administração e auditoria
- **Configurações dinâmicas** do sistema via interface admin
- **Gestão de perfil de usuário** com configurações personalizáveis
- **Notificações internas** para eventos do sistema

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Git

## ⚡ Instalação Rápida

```bash
# Clone o repositório
git clone <repository-url>
cd backend

# Execute o script de instalação
chmod +x install.sh
./install.sh
```

O script de instalação irá:
- Verificar dependências do sistema
- Criar ambiente virtual Python
- Instalar dependências
- Configurar banco de dados
- Criar usuário administrador
- Configurar serviços systemd (opcional)
- Configurar Nginx (opcional)

## � Execução com Docker

Para executar o sistema completo usando Docker:

```bash
# Iniciar todos os serviços
docker compose up -d

# Verificar status dos serviços
docker compose ps

# Verificar logs da aplicação
docker compose logs -f app
```

### Scripts Utilitários

Foram adicionados novos scripts para facilitar o desenvolvimento e testes:

```bash
# Executar testes em ambiente Docker
./run_tests_in_docker.sh

# Executar apenas um conjunto específico de testes
./run_tests_in_docker.sh tests/test_admin.py

# Verificar funcionamento de todos os endpoints
./verify_endpoints.sh

# Iniciar a aplicação com todos os serviços
./start.sh
```

```sql
-- PostgreSQL
CREATE DATABASE pncp_db;
CREATE USER pncp_user WITH ENCRYPTED PASSWORD 'pncp_password';
GRANT ALL PRIVILEGES ON DATABASE pncp_db TO pncp_user;
```

### 3. Variáveis de Ambiente

Crie um arquivo `.env`:

```env
# Database
DATABASE_URL=postgresql://pncp_user:pncp_password@localhost:5432/pncp_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-here
PNCP_WEBHOOK_SECRET=webhook-secret-key

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Application
DEBUG=False
LOG_LEVEL=INFO
```

### 4. Migrações do Banco

```bash
alembic upgrade head
```

### 5. Usuário Administrador

```bash
python -c "
from app.core.database import SessionLocal, init_db
from app.core.security import security_service
from app.models.usuario import Usuario

init_db()
db = SessionLocal()

admin_user = Usuario(
    username='admin',
    email='admin@sistema-pncp.gov.br',
    nome_completo='Administrador do Sistema',
    senha_hash=security_service.get_password_hash('admin123'),
    ativo=True,
    is_admin=True
)
db.add(admin_user)
db.commit()
db.close()
"
```

## 🚀 Execução

### Desenvolvimento

```bash
# API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Worker Celery
celery -A app.tasks worker --loglevel=info

# Scheduler Celery
celery -A app.tasks beat --loglevel=info
```

### Produção

```bash
# Habilitar serviços
sudo systemctl enable pncp-api pncp-worker pncp-beat

# Iniciar serviços
sudo systemctl start pncp-api pncp-worker pncp-beat

# Status dos serviços
sudo systemctl status pncp-api pncp-worker pncp-beat
```

## 📚 Documentação da API

Acesse a documentação interativa:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 📚 Endpoints API

A API segue padrões RESTful e está versionada (v1). Todos os endpoints estão disponíveis em `/api/v1/`.

### Endpoints Recém-Implementados

#### 1. Webhooks Internos

- **POST /webhooks/interno/notification** - Recebe notificações internas do sistema
  - Autenticação: Requerida
  - Rate limit: 50 requisições/minuto
  - Tipos de notificação suportados:
    - `contrato_vencendo` - Contrato próximo ao vencimento
    - `pca_atualizado` - PCA foi atualizado
    - `erro_sincronizacao` - Erro na sincronização com PNCP
    - `limite_orcamento` - Limite orçamentário atingido

#### 2. Endpoints de Administração

- **GET /admin/logs** - Lista logs do sistema com filtros e paginação
  - Autenticação: Requerida (apenas admin)
  - Rate limit: 50 requisições/minuto
  - Filtros disponíveis:
    - `nivel` - Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - `modulo` - Módulo/arquivo de origem
    - `data_inicio` e `data_fim` - Período de tempo
    - `termo_busca` - Busca na mensagem

- **GET /admin/configuracoes** - Lista configurações do sistema
  - Autenticação: Requerida (apenas admin)
  - Rate limit: 100 requisições/minuto
  - Filtros disponíveis:
    - `categoria` - Categoria das configurações

- **PUT /admin/configuracoes/{chave}** - Atualiza configuração específica
  - Autenticação: Requerida (apenas admin)
  - Rate limit: 10 requisições/minuto

#### 3. Endpoints de Perfil de Usuário

- **GET /usuarios/me/profile** - Obtém perfil do usuário atual
  - Autenticação: Requerida
  - Rate limit: 100 requisições/minuto

- **PUT /usuarios/me/profile** - Atualiza perfil do usuário atual
  - Autenticação: Requerida
  - Rate limit: 20 requisições/minuto
  - Campos atualizáveis:
    - `nome_completo`
    - `telefone`
    - `cargo`
    - `configuracoes`

- **POST /usuarios/{id}/change-password** - Altera senha de usuário
  - Autenticação: Requerida
  - Rate limit: 5 requisições/minuto
  - Permissões:
    - Usuários podem alterar apenas a própria senha
    - Administradores podem alterar senha de qualquer usuário

### Documentação Completa

Para a documentação completa da API, acesse:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## 🔗 Endpoints Principais

### Autenticação
- `POST /api/v1/auth/login` - Login do usuário
- `POST /api/v1/auth/logout` - Logout do usuário
- `GET /api/v1/auth/me` - Informações do usuário atual

### PCA (Planos Anuais de Contratação)
- `GET /api/v1/pca/search` - Buscar PCAs
- `GET /api/v1/pca/{id}` - Obter PCA específico
- `GET /api/v1/pca/sync` - Sincronizar PCAs

### Contratações
- `GET /api/v1/contratacoes/search` - Buscar contratações
- `GET /api/v1/contratacoes/{numero_controle}` - Obter contratação específica
- `GET /api/v1/contratacoes/sync` - Sincronizar contratações

### Atas de Registro de Preços
- `GET /api/v1/atas/search` - Buscar atas
- `GET /api/v1/atas/{numero_controle}` - Obter ata específica
- `GET /api/v1/atas/sync` - Sincronizar atas

### Contratos
- `GET /api/v1/contratos/search` - Buscar contratos
- `GET /api/v1/contratos/{numero_controle}` - Obter contrato específico
- `GET /api/v1/contratos/sync` - Sincronizar contratos

### Webhooks
- `POST /api/v1/webhooks/pncp` - Receber notificações do PNCP

### Administração
- `GET /api/v1/admin/health` - Status do sistema
- `GET /api/v1/admin/metrics` - Métricas do sistema
- `GET /api/v1/admin/logs` - Logs do sistema

## 🔧 Configuração Avançada

### Rate Limiting

Configure limites de requisições no `.env`:

```env
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Cache

Configurações de cache Redis:

```env
CACHE_TTL=3600
DOMAIN_CACHE_TTL=86400
```

### Logs

Configuração de logs estruturados:

```env
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Sincronização

Configurações do Celery para sincronização:

```env
SYNC_INTERVAL_MINUTES=30
DAILY_SYNC_HOUR=6
BATCH_SIZE=100
```

## 🔍 Monitoramento

### Health Check

```bash
curl http://localhost:8000/health
```

### Métricas

```bash
curl http://localhost:8000/api/v1/admin/metrics
```

### Logs

Os logs são estruturados em JSON e incluem:
- Timestamp
- Nível (INFO, WARNING, ERROR)
- Categoria (AUTH, API, SYNC, SYSTEM)
- Mensagem
- Contexto adicional

## 🛡️ Segurança

### Autenticação

- JWT tokens com expiração configurável
- Senhas hasheadas com bcrypt
- Rate limiting por usuário/IP

### Autorização

- Perfis de usuário (admin, gestor, operador)
- Controle de acesso por endpoint
- Validação de permissões

### Webhooks

- Validação HMAC de assinaturas
- Processamento assíncrono
- Retry automático com backoff

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Testes com cobertura
pytest --cov=app --cov-report=html

# Testes de integração
pytest tests/integration/

# Testes unitários
pytest tests/unit/
```

## 📊 Performance

### Otimizações Implementadas

- **Cache em múltiplas camadas** (Redis + aplicação)
- **Conexões persistentes** com pool de conexões
- **Queries otimizadas** com índices estratégicos
- **Compressão de respostas** (gzip)
- **Paginação eficiente** com limites configuráveis

### Métricas de Performance

- Tempo médio de resposta: < 200ms
- Throughput: > 1000 req/s
- Cache hit rate: > 80%
- Sincronização: 99.9% de sucesso

## 🔄 Sincronização com PNCP

### Estratégias de Sincronização

1. **Sincronização Diária**: Todos os dias às 6h
2. **Sincronização em Tempo Real**: Via webhooks
3. **Sincronização Manual**: Endpoints dedicados
4. **Sincronização de Recuperação**: Para dados perdidos

### Tipos de Dados Sincronizados

- Planos Anuais de Contratação (PCA)
- Contratações públicas
- Atas de registro de preços
- Contratos administrativos
- Tabelas de domínio

## 🚨 Troubleshooting

### Problemas Comuns

#### Erro de Conexão com PostgreSQL
```bash
# Verificar se o PostgreSQL está rodando
sudo systemctl status postgresql

# Verificar logs
sudo journalctl -u postgresql
```

#### Erro de Conexão com Redis
```bash
# Verificar se o Redis está rodando
sudo systemctl status redis

# Testar conexão
redis-cli ping
```

#### Problemas de Sincronização
```bash
# Verificar logs do Celery
sudo journalctl -u pncp-worker

# Reiniciar workers
sudo systemctl restart pncp-worker pncp-beat
```

### Logs Importantes

```bash
# Logs da API
sudo journalctl -u pncp-api -f

# Logs do worker
sudo journalctl -u pncp-worker -f

# Logs do scheduler
sudo journalctl -u pncp-beat -f
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Suporte

Para suporte técnico:
- 📧 Email: suporte@sistema-pncp.gov.br
- 📖 Documentação: [Link para documentação completa]
- 🐛 Issues: [Link para issues do GitHub]

## 📈 Roadmap

### Versão 1.1
- [ ] Dashboard de métricas em tempo real
- [ ] Exportação avançada de dados
- [ ] Integração com sistemas de BI

### Versão 1.2
- [ ] API GraphQL
- [ ] Notificações por email
- [ ] Auditoria avançada

### Versão 2.0
- [ ] Machine Learning para análise de dados
- [ ] API para dispositivos móveis
- [ ] Integração com blockchain

---

**Desenvolvido com ❤️ para a Administração Pública Brasileira**
