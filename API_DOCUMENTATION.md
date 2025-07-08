# API Documentation - SEARCB Backend

## Visão Geral

O backend SEARCB é um sistema completo para gestão de contratações públicas integrado ao Portal Nacional de Contratações Públicas (PNCP), desenvolvido com Python, FastAPI, SQLAlchemy, PostgreSQL, Redis e Celery.

## Arquitetura

### Componentes Principais

- **FastAPI**: Framework web moderno para APIs Python
- **SQLAlchemy**: ORM para interação com banco de dados
- **PostgreSQL**: Banco de dados### Rate Limiting

### Limites por Endpoint

Os limites de requisições são configurados para os seguintes endpoints:

- **Endpoints GET**: 100 requisições/minuto
- **GET /usuarios**: 100 requisições/hora
- **Outros endpoints**: Podem ter limites específicos configurados

### Configuração

Rate limiting é configurado por usuário usando Redis como backend. O middleware de rate limiting está implementado em `app/middleware/rate_limiting.py`.principal
- **Redis**: Cache e broker para tarefas assíncronas
- **Celery**: Processamento de tarefas em background
- **Alembic**: Migrações de banco de dados

### Estrutura de Diretórios

```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/           # Endpoints da API
│   │   └── router.py           # Roteamento principal
│   ├── core/
│   │   ├── config.py           # Configurações
│   │   ├── database.py         # Conexão com banco
│   │   ├── security.py         # Autenticação/autorização
│   │   └── cache.py            # Cache Redis
│   ├── models/                 # Modelos do banco de dados
│   ├── schemas/                # Schemas Pydantic
│   ├── services/               # Lógica de negócio
│   ├── tasks/                  # Tarefas Celery
│   ├── utils/                  # Utilitários
│   ├── middleware/             # Middlewares
│   └── main.py                 # Aplicação principal
├── tests/                      # Testes
├── migrations/                 # Migrações Alembic
└── requirements.txt           # Dependências
```

## Configuração

### Variáveis de Ambiente

```env
# Banco de dados
DATABASE_URL=postgresql://user:password@localhost/searcb_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Segurança
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# PNCP
PNCP_API_URL=https://api.gov.br/pncp/v1
PNCP_TOKEN=your-pncp-token

# Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Instalação

```bash
# Clonar repositório
git clone <repository-url>
cd searcb/backend

# Instalar dependências
pip install -r requirements.txt

# Executar migrações
alembic upgrade head

# Iniciar aplicação
uvicorn app.main:app --reload
```

## Endpoints da API

### Autenticação

#### POST /auth/login
Autentica um usuário e retorna token de acesso.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "user@example.com",
    "nome_completo": "João Silva",
    "is_admin": false
  }
}
```

### PCAs (Planos de Contratação Anual)

#### GET /pca
Lista PCAs com filtros e paginação.

**Query Parameters:**
- `page`: Número da página (padrão: 1)
- `size`: Tamanho da página (padrão: 10, máximo: 100)
- `ano`: Ano do PCA
- `orgao_cnpj`: CNPJ do órgão
- `status`: Status do PCA
- `termo_busca`: Termo de busca livre
- `data_inicio`: Data de início (formato: YYYY-MM-DD)
- `data_fim`: Data de fim (formato: YYYY-MM-DD)
- `valor_minimo`: Valor mínimo
- `valor_maximo`: Valor máximo
- `ordenar_por`: Campo para ordenação (data_publicacao, valor_total)

**Example Request:**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/pca?page=1&size=20&ano=2024"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "ano": 2024,
      "orgao_cnpj": "12345678901234",
      "orgao_nome": "Ministério da Educação",
      "numero_pca": "PCA-2024-001",
      "status": "PUBLICADO",
      "valor_total": 1000000.00,
      "data_publicacao": "2024-01-15T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

#### GET /pca/{id}
Obtém detalhes de um PCA específico.

#### POST /pca
Cria um novo PCA.

**Request Body:**
```json
{
  "ano": 2024,
  "orgao_cnpj": "12345678901234",
  "orgao_nome": "Ministério da Educação",
  "numero_pca": "PCA-2024-001",
  "titulo": "Plano de Contratação Anual 2024",
  "descricao": "Plano para contratações do exercício 2024",
  "valor_total": 1000000.00,
  "data_publicacao": "2024-01-15"
}
```

#### PUT /pca/{id}
Atualiza um PCA existente.

#### DELETE /pca/{id}
Remove um PCA.

### Contratações

#### GET /contratacoes
Lista contratações com filtros e paginação.

**Query Parameters:**
- `page`: Número da página (padrão: 1)
- `size`: Tamanho da página (padrão: 10, máximo: 100)
- `ano`: Ano da contratação
- `modalidade`: Modalidade da contratação
- `situacao`: Situação da contratação
- `orgao_cnpj`: CNPJ do órgão
- `data_inicio`: Data de início (formato: YYYY-MM-DD)
- `data_fim`: Data de fim (formato: YYYY-MM-DD)
- `valor_minimo`: Valor mínimo estimado
- `valor_maximo`: Valor máximo estimado
- `termo_busca`: Termo de busca (objeto, número ou órgão)
- `ordenar_por`: Campo para ordenação (data_abertura, valor_estimado)

#### GET /contratacoes/{id}
Obtém detalhes de uma contratação específica.

#### POST /contratacoes
Cria nova contratação.

#### PUT /contratacoes/{id}
Atualiza contratação existente.

#### DELETE /contratacoes/{id}
Remove contratação.

### Atas de Registro de Preços

#### GET /atas
Lista atas com filtros e paginação.

**Query Parameters:**
- `page`: Número da página (padrão: 1)
- `size`: Tamanho da página (padrão: 10, máximo: 100)
- `ano`: Ano da ata
- `orgao_cnpj`: CNPJ do órgão
- `situacao`: Situação da ata
- `data_inicio`: Data de publicação inicial (formato: YYYY-MM-DD)
- `data_fim`: Data de publicação final (formato: YYYY-MM-DD)
- `valor_minimo`: Valor mínimo total
- `valor_maximo`: Valor máximo total
- `vigencia_inicio`: Data de início da vigência (formato: YYYY-MM-DD)
- `vigencia_fim`: Data de fim da vigência (formato: YYYY-MM-DD)
- `termo_busca`: Termo de busca (objeto, número ou órgão)
- `ordenar_por`: Campo para ordenação (data_publicacao, valor_total, vigencia)

#### GET /atas/{id}
Obtém detalhes de uma ata específica.

#### POST /atas
Cria nova ata.

#### PUT /atas/{id}
Atualiza ata existente.

#### DELETE /atas/{id}
Remove ata.

### Contratos

#### GET /contratos
Lista contratos com filtros e paginação.

**Query Parameters:**
- `page`: Número da página (padrão: 1)
- `size`: Tamanho da página (padrão: 10, máximo: 100)
- `ano`: Ano do contrato
- `orgao_cnpj`: CNPJ do órgão
- `fornecedor_cnpj`: CNPJ do fornecedor
- `situacao`: Situação do contrato
- `data_inicio`: Data de assinatura inicial (formato: YYYY-MM-DD)
- `data_fim`: Data de assinatura final (formato: YYYY-MM-DD)
- `valor_minimo`: Valor mínimo do contrato
- `valor_maximo`: Valor máximo do contrato
- `vigencia_inicio`: Data de início da vigência (formato: YYYY-MM-DD)
- `vigencia_fim`: Data de fim da vigência (formato: YYYY-MM-DD)
- `termo_busca`: Termo de busca (objeto, número, órgão ou fornecedor)
- `ordenar_por`: Campo para ordenação (data_assinatura, valor_inicial, vigencia)

#### GET /contratos/{id}
Obtém detalhes de um contrato específico.

#### POST /contratos
Cria novo contrato.

#### PUT /contratos/{id}
Atualiza contrato existente.

#### DELETE /contratos/{id}
Remove contrato.

### Usuários

#### GET /usuarios
Lista usuários (apenas administradores).

**Query Parameters:**
- `page`: Número da página (padrão: 1)
- `size`: Tamanho da página (padrão: 20, máximo: 100)
- `search`: Busca por username, email ou nome
- `ativo`: Filtrar por status ativo
- `is_admin`: Filtrar por administradores
- `orgao_cnpj`: Filtrar por CNPJ do órgão

#### GET /usuarios/{id}
Obtém detalhes de um usuário.

#### POST /usuarios
Cria novo usuário (apenas administradores).

#### PUT /usuarios/{id}
Atualiza usuário.

#### DELETE /usuarios/{id}
Remove usuário (apenas administradores).

**Observação**: Os endpoints de perfil de usuário e alteração de senha podem estar implementados em um módulo separado ou ainda estão em desenvolvimento.

### Webhooks

#### POST /webhooks/pncp/notification
Recebe notificações do PNCP.

**Observação**: Este endpoint verifica a assinatura da requisição usando HMAC com SHA-256 para garantir a autenticidade das notificações do PNCP.

### Administração

#### GET /admin/dashboard
Obtém dados do dashboard administrativo.

**Response:**
```json
{
  "estatisticas_gerais": {
    "total_pcas": 120,
    "total_contratacoes": 450,
    "total_atas": 75,
    "total_contratos": 310,
    "total_usuarios": 85,
    "valor_total_contratos": 25000000.00
  },
  "estatisticas_periodo": {
    "pcas_30_dias": 15,
    "contratacoes_30_dias": 45,
    "atas_30_dias": 10,
    "contratos_30_dias": 25
  },
  "alertas": {
    "contratos_vencendo": 12
  },
  "top_orgaos": [
    {
      "orgao_nome": "Ministério da Educação",
      "valor_total": 5000000.00,
      "total_contratos": 45
    },
    // ... outros órgãos
  ],
  "stats_modalidade": [
    {
      "modalidade": "PREGÃO",
      "quantidade": 200,
      "valor": 15000000.00
    },
    // ... outras modalidades
  ]
}
```

## Autenticação e Autorização

### Fluxo de Autenticação

1. **Login**: Usuario envia credenciais para `/auth/login`
2. **Token**: Sistema retorna JWT token
3. **Autorização**: Token deve ser incluído no header `Authorization: Bearer <token>`
4. **Validação**: Sistema valida token em cada requisição

**Resposta de Login**:
```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 1,
      "username": "user@example.com",
      "email": "user@example.com",
      "nome_completo": "João Silva",
      "is_admin": false,
      "is_gestor": true,
      "is_operador": true
    }
  }
}
```

### Níveis de Acesso

- **Administrador**: Acesso total ao sistema
- **Gestor**: Acesso de leitura/escrita limitado
- **Operador**: Acesso de leitura apenas

## Cache

### Estratégia de Cache

O sistema utiliza Redis para cache com as seguintes estratégias:

- **Cache de consultas**: Resultados de consultas frequentes
- **Cache de sessão**: Informações de usuários logados
- **Cache de dados externos**: Dados do PNCP
- **TTL configurável**: Tempo de vida ajustável por tipo de dados

### Invalidação de Cache

- **Automática**: Por TTL definido
- **Manual**: Via endpoints administrativos
- **Por eventos**: Invalidação baseada em mudanças de dados

## Processamento Assíncrono

### Tarefas Celery

#### Sincronização com PNCP
- **Frequência**: Diária
- **Horário**: 01:00 AM
- **Função**: Sincronizar dados do PNCP

#### Limpeza de Cache
- **Frequência**: A cada 6 horas
- **Função**: Remover entradas expiradas

#### Verificação de Contratos
- **Frequência**: Diária
- **Função**: Verificar contratos próximos ao vencimento

#### Relatórios
- **Frequência**: Diária
- **Função**: Gerar relatórios automáticos

### Monitoramento

#### Celery Flower
Interface web para monitoramento de tarefas Celery.

```bash
# Iniciar Flower
celery -A app.tasks.sync_tasks flower --port=5555
```

Acessar: http://localhost:5555

## Rate Limiting

### Limites por Endpoint

- **GET**: 100 requisições/minuto
- **POST**: 10 requisições/minuto
- **PUT**: 10 requisições/minuto
- **DELETE**: 5 requisições/minuto

### Configuração

Rate limiting é configurado por usuário usando Redis como backend.

## Logging

### Níveis de Log

- **DEBUG**: Informações detalhadas para debug
- **INFO**: Informações gerais de funcionamento
- **WARNING**: Situações que merecem atenção
- **ERROR**: Erros que não quebram a aplicação
- **CRITICAL**: Erros críticos que podem quebrar a aplicação

### Estrutura de Log

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "INFO",
  "module": "app.api.endpoints.pca",
  "message": "PCA criado com sucesso",
  "user_id": 1,
  "request_id": "req-123",
  "details": {
    "pca_id": 1,
    "duration_ms": 150
  }
}
```

## Monitoramento e Métricas

### Health Check

#### GET /health
Verifica saúde da aplicação.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1593536400,
  "version": "1.0.0",
  "components": {
    "database": {"status": "healthy"},
    "cache": {"status": "healthy"}
  }
}
```

### Métricas

- **Tempo de resposta**: Tempo médio de resposta por endpoint
- **Taxa de erro**: Percentual de requisições com erro
- **Throughput**: Número de requisições por segundo
- **Uso de recursos**: CPU, memória, conexões de banco

## Segurança

### Medidas de Segurança

- **JWT Authentication**: Tokens seguros para autenticação
- **Password Hashing**: Senhas hasheadas com bcrypt
- **CORS**: Configuração de CORS para acesso cross-origin
- **Rate Limiting**: Proteção contra abuso de API
- **Input Validation**: Validação rigorosa de entrada
- **SQL Injection Protection**: Uso de ORM previne injeção SQL
- **XSS Protection**: Headers de segurança configurados

### Headers de Segurança

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/searcb
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=searcb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A app.tasks.sync_tasks worker --loglevel=info
    depends_on:
      - redis
      - db

volumes:
  postgres_data:
```

## Testes

### Executar Testes

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/test_integration.py

# Com coverage
pytest --cov=app tests/
```

### Tipos de Testes

- **Testes unitários**: Testam componentes isolados
- **Testes de integração**: Testam fluxos completos
- **Testes de API**: Testam endpoints HTTP
- **Testes de performance**: Testam carga e performance

## Troubleshooting

### Problemas Comuns

#### Erro de Conexão com Banco
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Verificar conectividade
pg_isready -h localhost -p 5432
```

#### Erro de Conexão com Redis
```bash
# Verificar se Redis está rodando
redis-cli ping
```

#### Problemas de Autenticação
- Verificar se SECRET_KEY está configurada
- Verificar se token não expirou
- Verificar se usuário está ativo

#### Problemas de Performance
- Verificar queries lentas no banco
- Verificar hit rate do cache
- Verificar uso de recursos do sistema

## Notas de Implementação

Este documento descreve a API SEARCB conforme a especificação original. Alguns endpoints e funcionalidades documentados aqui podem:

- Estar em desenvolvimento e ainda não implementados completamente
- Ter sido modificados durante a implementação
- Ter comportamentos ou parâmetros diferentes dos descritos

É recomendado consultar a documentação interativa da API em `/api/v1/docs` para obter a documentação mais atualizada dos endpoints disponíveis e seus parâmetros.

## Contato e Suporte

Para dúvidas ou suporte:
- **Email**: suporte@searcb.gov.br
- **Documentação**: https://docs.searcb.gov.br
- **Issues**: https://github.com/searcb/backend/issues
