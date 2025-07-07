# Plano Completo do Banco de Dados - Sistema PNCP

## 1. Visão Geral da Arquitetura

### 1.1 Tecnologias Principais
- **SGBD**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0 (Python)
- **Migrations**: Alembic
- **Connection Pool**: pgbouncer
- **Cache**: Redis 7.0+
- **Backup**: pg_dump + AWS S3/MinIO

### 1.2 Estrutura de Ambientes
```
├── desenvolvimento (local)
├── homologação (staging)
├── produção (production)
└── disaster_recovery (DR)
```

## 2. Modelagem de Dados

### 2.1 Diagrama ERD - Principais Entidades

```sql
-- Entidades Principais
PCA ──┬── ItemPCA
      └── OrgaoEntidade

Contratacao ──┬── ItemContratacao
              ├── OrgaoEntidade
              └── UnidadeOrgao

AtaRegistroPreco ──┬── ItemAta
                   └── OrgaoEntidade

Contrato ──┬── ItemContrato
           ├── OrgaoEntidade
           └── Fornecedor

-- Entidades de Apoio
Usuario
AuditLog
ConfiguracaoSistema
TabelaDominio
```

### 2.2 Tabelas de Domínio (Lookup Tables)

```sql
-- Tabela genérica para códigos de domínio do PNCP
CREATE TABLE tabela_dominio (
    id SERIAL PRIMARY KEY,
    categoria VARCHAR(50) NOT NULL, -- 'modalidade', 'situacao', 'amparo_legal', etc.
    codigo INTEGER NOT NULL,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(categoria, codigo)
);

-- Índices para performance
CREATE INDEX idx_tabela_dominio_categoria ON tabela_dominio(categoria);
CREATE INDEX idx_tabela_dominio_codigo ON tabela_dominio(codigo);
```

## 3. Estrutura Detalhada das Tabelas

### 3.1 Tabela: orgao_entidade

```sql
CREATE TABLE orgao_entidade (
    id SERIAL PRIMARY KEY,
    cnpj VARCHAR(14) NOT NULL UNIQUE,
    razao_social VARCHAR(255) NOT NULL,
    nome_fantasia VARCHAR(255),
    poder_id CHAR(1), -- L=Legislativo, E=Executivo, J=Judiciário
    esfera_id CHAR(1), -- F=Federal, E=Estadual, M=Municipal, D=Distrital
    codigo_ibge INTEGER,
    municipio VARCHAR(100),
    uf_sigla CHAR(2),
    uf_nome VARCHAR(50),
    situacao_ativa BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_orgao_cnpj ON orgao_entidade(cnpj);
CREATE INDEX idx_orgao_uf ON orgao_entidade(uf_sigla);
CREATE INDEX idx_orgao_municipio ON orgao_entidade(municipio);
```

### 3.2 Tabela: unidade_orgao

```sql
CREATE TABLE unidade_orgao (
    id SERIAL PRIMARY KEY,
    orgao_id INTEGER REFERENCES orgao_entidade(id),
    codigo_unidade VARCHAR(20) NOT NULL,
    nome_unidade VARCHAR(255) NOT NULL,
    codigo_ibge INTEGER,
    municipio VARCHAR(100),
    uf_sigla CHAR(2),
    uf_nome VARCHAR(50),
    situacao_ativa BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(orgao_id, codigo_unidade)
);

-- Índices
CREATE INDEX idx_unidade_orgao_codigo ON unidade_orgao(codigo_unidade);
CREATE INDEX idx_unidade_orgao_nome ON unidade_orgao(nome_unidade);
```

### 3.3 Tabela: pca (Plano de Contratações Anual)

```sql
CREATE TABLE pca (
    id SERIAL PRIMARY KEY,
    id_pca_pncp VARCHAR(50) NOT NULL UNIQUE,
    ano_pca INTEGER NOT NULL,
    data_publicacao_pncp DATE,
    orgao_id INTEGER REFERENCES orgao_entidade(id),
    unidade_id INTEGER REFERENCES unidade_orgao(id),
    situacao VARCHAR(50) DEFAULT 'ATIVO',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_sincronizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_pca_ano ON pca(ano_pca);
CREATE INDEX idx_pca_orgao ON pca(orgao_id);
CREATE INDEX idx_pca_publicacao ON pca(data_publicacao_pncp);
CREATE INDEX idx_pca_pncp_id ON pca(id_pca_pncp);
```

### 3.4 Tabela: item_pca

```sql
CREATE TABLE item_pca (
    id SERIAL PRIMARY KEY,
    pca_id INTEGER REFERENCES pca(id) ON DELETE CASCADE,
    numero_item INTEGER NOT NULL,
    categoria_item_pca_id INTEGER,
    categoria_item_pca_nome VARCHAR(100),
    classificacao_catalogo_id VARCHAR(10),
    nome_classificacao_catalogo VARCHAR(50),
    classificacao_superior_codigo VARCHAR(100),
    classificacao_superior_nome VARCHAR(255),
    pdm_codigo VARCHAR(100),
    pdm_descricao VARCHAR(255),
    codigo_item VARCHAR(100),
    descricao_item TEXT,
    unidade_fornecimento VARCHAR(20),
    quantidade_estimada DECIMAL(15,4),
    valor_unitario DECIMAL(15,4),
    valor_total DECIMAL(15,4),
    valor_orcamento_exercicio DECIMAL(15,4),
    data_desejada DATE,
    unidade_requisitante VARCHAR(255),
    grupo_contratacao_codigo VARCHAR(50),
    grupo_contratacao_nome VARCHAR(255),
    data_inclusao DATE,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pca_id, numero_item)
);

-- Índices
CREATE INDEX idx_item_pca_categoria ON item_pca(categoria_item_pca_id);
CREATE INDEX idx_item_pca_classificacao ON item_pca(classificacao_superior_codigo);
CREATE INDEX idx_item_pca_valor ON item_pca(valor_total);
CREATE INDEX idx_item_pca_descricao ON item_pca USING gin(to_tsvector('portuguese', descricao_item));
```

### 3.5 Tabela: contratacao

```sql
CREATE TABLE contratacao (
    id SERIAL PRIMARY KEY,
    numero_controle_pncp VARCHAR(50) NOT NULL UNIQUE,
    numero_compra VARCHAR(50),
    ano_compra INTEGER,
    processo VARCHAR(50),
    
    -- Instrumento e modalidade
    tipo_instrumento_convocatorio_id INTEGER,
    tipo_instrumento_convocatorio_nome VARCHAR(100),
    modalidade_id INTEGER NOT NULL,
    modalidade_nome VARCHAR(100),
    modo_disputa_id INTEGER,
    modo_disputa_nome VARCHAR(100),
    
    -- Situação
    situacao_compra_id INTEGER,
    situacao_compra_nome VARCHAR(100),
    
    -- Objeto
    objeto_compra TEXT,
    informacao_complementar TEXT,
    srp BOOLEAN DEFAULT FALSE,
    
    -- Amparo legal
    amparo_legal_codigo INTEGER,
    amparo_legal_nome VARCHAR(255),
    amparo_legal_descricao TEXT,
    
    -- Valores
    valor_total_estimado DECIMAL(15,4),
    valor_total_homologado DECIMAL(15,4),
    
    -- Datas
    data_abertura_proposta TIMESTAMP,
    data_encerramento_proposta TIMESTAMP,
    data_publicacao_pncp DATE,
    data_inclusao DATE,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Controle
    sequencial_compra INTEGER,
    
    -- Órgão/Entidade
    orgao_id INTEGER REFERENCES orgao_entidade(id),
    unidade_id INTEGER REFERENCES unidade_orgao(id),
    
    -- Órgão subrogado (opcional)
    orgao_subrogado_id INTEGER REFERENCES orgao_entidade(id),
    unidade_subrogada_id INTEGER REFERENCES unidade_orgao(id),
    
    -- Sistema
    usuario_nome VARCHAR(255),
    link_sistema_origem VARCHAR(500),
    justificativa_presencial TEXT,
    
    -- Controle interno
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_sincronizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices principais
CREATE INDEX idx_contratacao_pncp ON contratacao(numero_controle_pncp);
CREATE INDEX idx_contratacao_modalidade ON contratacao(modalidade_id);
CREATE INDEX idx_contratacao_situacao ON contratacao(situacao_compra_id);
CREATE INDEX idx_contratacao_publicacao ON contratacao(data_publicacao_pncp);
CREATE INDEX idx_contratacao_encerramento ON contratacao(data_encerramento_proposta);
CREATE INDEX idx_contratacao_orgao ON contratacao(orgao_id);
CREATE INDEX idx_contratacao_ano ON contratacao(ano_compra);
CREATE INDEX idx_contratacao_valor ON contratacao(valor_total_estimado);
CREATE INDEX idx_contratacao_objeto ON contratacao USING gin(to_tsvector('portuguese', objeto_compra));
```

### 3.6 Tabela: item_contratacao

```sql
CREATE TABLE item_contratacao (
    id SERIAL PRIMARY KEY,
    contratacao_id INTEGER REFERENCES contratacao(id) ON DELETE CASCADE,
    numero_item INTEGER NOT NULL,
    descricao_item TEXT,
    unidade_medida VARCHAR(20),
    quantidade DECIMAL(15,4),
    valor_unitario DECIMAL(15,4),
    valor_total DECIMAL(15,4),
    situacao_item_id INTEGER,
    situacao_item_nome VARCHAR(100),
    tipo_beneficio_id INTEGER,
    tipo_beneficio_nome VARCHAR(100),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(contratacao_id, numero_item)
);

-- Índices
CREATE INDEX idx_item_contratacao_situacao ON item_contratacao(situacao_item_id);
CREATE INDEX idx_item_contratacao_beneficio ON item_contratacao(tipo_beneficio_id);
CREATE INDEX idx_item_contratacao_valor ON item_contratacao(valor_total);
```

### 3.7 Tabela: ata_registro_preco

```sql
CREATE TABLE ata_registro_preco (
    id SERIAL PRIMARY KEY,
    numero_controle_pncp_ata VARCHAR(50) NOT NULL UNIQUE,
    numero_controle_pncp_compra VARCHAR(50),
    numero_ata_registro_preco VARCHAR(50),
    ano_ata INTEGER,
    
    -- Datas
    data_assinatura DATE,
    vigencia_inicio DATE,
    vigencia_fim DATE,
    data_cancelamento DATE,
    cancelado BOOLEAN DEFAULT FALSE,
    data_publicacao_pncp DATE,
    data_inclusao DATE,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Objeto
    objeto_contratacao TEXT,
    
    -- Órgão
    orgao_id INTEGER REFERENCES orgao_entidade(id),
    unidade_id INTEGER REFERENCES unidade_orgao(id),
    
    -- Órgão subrogado (opcional)
    orgao_subrogado_id INTEGER REFERENCES orgao_entidade(id),
    unidade_subrogada_id INTEGER REFERENCES unidade_orgao(id),
    
    -- Sistema
    usuario VARCHAR(255),
    
    -- Controle interno
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_sincronizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_ata_pncp_ata ON ata_registro_preco(numero_controle_pncp_ata);
CREATE INDEX idx_ata_pncp_compra ON ata_registro_preco(numero_controle_pncp_compra);
CREATE INDEX idx_ata_ano ON ata_registro_preco(ano_ata);
CREATE INDEX idx_ata_vigencia ON ata_registro_preco(vigencia_inicio, vigencia_fim);
CREATE INDEX idx_ata_orgao ON ata_registro_preco(orgao_id);
```

### 3.8 Tabela: contrato

```sql
CREATE TABLE contrato (
    id SERIAL PRIMARY KEY,
    numero_controle_pncp VARCHAR(50) NOT NULL UNIQUE,
    numero_controle_pncp_compra VARCHAR(50),
    numero_contrato_empenho VARCHAR(50),
    ano_contrato INTEGER,
    sequencial_contrato INTEGER,
    processo VARCHAR(50),
    
    -- Tipo e categoria
    tipo_contrato_id INTEGER,
    tipo_contrato_nome VARCHAR(100),
    categoria_processo_id INTEGER,
    categoria_processo_nome VARCHAR(100),
    
    -- Natureza
    receita BOOLEAN DEFAULT FALSE,
    
    -- Objeto
    objeto_contrato TEXT,
    informacao_complementar TEXT,
    
    -- Órgão/Entidade
    orgao_id INTEGER REFERENCES orgao_entidade(id),
    unidade_id INTEGER REFERENCES unidade_orgao(id),
    
    -- Órgão subrogado
    orgao_subrogado_id INTEGER REFERENCES orgao_entidade(id),
    unidade_subrogada_id INTEGER REFERENCES unidade_orgao(id),
    
    -- Fornecedor
    fornecedor_id INTEGER REFERENCES fornecedor(id),
    
    -- Subcontratado (opcional)
    subcontratado_id INTEGER REFERENCES fornecedor(id),
    
    -- Valores
    valor_inicial DECIMAL(15,4),
    numero_parcelas INTEGER,
    valor_parcela DECIMAL(15,4),
    valor_global DECIMAL(15,4),
    valor_acumulado DECIMAL(15,4),
    
    -- Datas
    data_assinatura DATE,
    data_vigencia_inicio DATE,
    data_vigencia_fim DATE,
    data_publicacao_pncp TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Controle
    numero_retificacao INTEGER DEFAULT 0,
    
    -- Sistema
    usuario_nome VARCHAR(255),
    
    -- CIPI (opcional)
    identificador_cipi VARCHAR(100),
    url_cipi VARCHAR(500),
    
    -- Controle interno
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_sincronizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_contrato_pncp ON contrato(numero_controle_pncp);
CREATE INDEX idx_contrato_compra ON contrato(numero_controle_pncp_compra);
CREATE INDEX idx_contrato_ano ON contrato(ano_contrato);
CREATE INDEX idx_contrato_vigencia ON contrato(data_vigencia_inicio, data_vigencia_fim);
CREATE INDEX idx_contrato_orgao ON contrato(orgao_id);
CREATE INDEX idx_contrato_fornecedor ON contrato(fornecedor_id);
CREATE INDEX idx_contrato_valor ON contrato(valor_global);
```

### 3.9 Tabela: fornecedor

```sql
CREATE TABLE fornecedor (
    id SERIAL PRIMARY KEY,
    tipo_pessoa CHAR(2) NOT NULL, -- PF, PJ
    ni_fornecedor VARCHAR(30) NOT NULL, -- CPF ou CNPJ
    nome_razao_social VARCHAR(255) NOT NULL,
    nome_fantasia VARCHAR(255),
    porte_empresa_id INTEGER,
    porte_empresa_nome VARCHAR(100),
    natureza_juridica_id INTEGER,
    natureza_juridica_nome VARCHAR(255),
    situacao_ativa BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ni_fornecedor)
);

-- Índices
CREATE INDEX idx_fornecedor_ni ON fornecedor(ni_fornecedor);
CREATE INDEX idx_fornecedor_nome ON fornecedor(nome_razao_social);
CREATE INDEX idx_fornecedor_porte ON fornecedor(porte_empresa_id);
```

### 3.10 Tabela: usuario

```sql
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    nome_completo VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    orgao_id INTEGER REFERENCES orgao_entidade(id),
    perfil_acesso VARCHAR(50) DEFAULT 'CONSULTA', -- CONSULTA, GESTOR, ADMIN
    ultimo_login TIMESTAMP,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_usuario_email ON usuario(email);
CREATE INDEX idx_usuario_orgao ON usuario(orgao_id);
CREATE INDEX idx_usuario_perfil ON usuario(perfil_acesso);
```

### 3.11 Tabela: audit_log

```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    tabela VARCHAR(100) NOT NULL,
    registro_id INTEGER NOT NULL,
    operacao VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    dados_anteriores JSONB,
    dados_novos JSONB,
    usuario_id INTEGER REFERENCES usuario(id),
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_audit_log_tabela ON audit_log(tabela);
CREATE INDEX idx_audit_log_registro ON audit_log(registro_id);
CREATE INDEX idx_audit_log_usuario ON audit_log(usuario_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
```

## 4. Configuração e Otimização

### 4.1 Configuração do PostgreSQL

```sql
-- postgresql.conf (principais parâmetros)
max_connections = 200
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 16MB
maintenance_work_mem = 512MB
checkpoint_timeout = 10min
max_wal_size = 2GB
min_wal_size = 80MB
log_min_duration_statement = 1000ms
log_statement = 'ddl'
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### 4.2 Particionamento de Tabelas

```sql
-- Particionamento da tabela contratacao por ano
CREATE TABLE contratacao_2024 PARTITION OF contratacao
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE contratacao_2025 PARTITION OF contratacao
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Particionamento da tabela audit_log por mês
CREATE TABLE audit_log_2024_01 PARTITION OF audit_log
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 4.3 Índices Compostos e Especializados

```sql
-- Índice composto para consultas complexas
CREATE INDEX idx_contratacao_modalidade_data ON contratacao(modalidade_id, data_publicacao_pncp);

-- Índice parcial para registros ativos
CREATE INDEX idx_contratacao_ativa ON contratacao(data_publicacao_pncp) 
WHERE situacao_compra_id IN (1, 4);

-- Índice GIN para busca textual
CREATE INDEX idx_contratacao_busca_texto ON contratacao 
USING gin(to_tsvector('portuguese', objeto_compra || ' ' || COALESCE(informacao_complementar, '')));

-- Índice para consultas de valor
CREATE INDEX idx_contratacao_valor_range ON contratacao(valor_total_estimado) 
WHERE valor_total_estimado > 0;
```

## 5. Estratégias de Backup e Recuperação

### 5.1 Backup Completo Diário

```bash
#!/bin/bash
# Script de backup completo
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgresql"
DATABASE="pncp_db"

# Backup completo
pg_dump -h localhost -U postgres -d $DATABASE -f "$BACKUP_DIR/full_backup_$DATE.sql"

# Compressão
gzip "$BACKUP_DIR/full_backup_$DATE.sql"

# Upload para S3/MinIO
aws s3 cp "$BACKUP_DIR/full_backup_$DATE.sql.gz" s3://pncp-backups/daily/

# Limpeza de backups antigos (manter últimos 7 dias)
find $BACKUP_DIR -name "full_backup_*.sql.gz" -mtime +7 -delete
```

### 5.2 Backup Incremental (WAL)

```sql
-- Configuração para backup incremental
archive_mode = on
archive_command = 'cp %p /backups/postgresql/wal/%f'
wal_level = replica
```

### 5.3 Plano de Recuperação de Desastres

```sql
-- Cenário 1: Recuperação point-in-time
-- 1. Restaurar último backup completo
-- 2. Aplicar WAL logs até o ponto desejado

-- Cenário 2: Replicação para DR
-- Configurar streaming replication
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'senha_segura';
```

## 6. Monitoramento e Manutenção

### 6.1 Consultas de Monitoramento

```sql
-- Tamanho das tabelas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Índices não utilizados
SELECT 
    schemaname, 
    tablename, 
    indexname, 
    idx_scan, 
    idx_tup_read, 
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY schemaname, tablename;

-- Consultas lentas
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

### 6.2 Manutenção Automática

```sql
-- Configurar autovacuum
autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 1min
autovacuum_vacuum_threshold = 50
autovacuum_analyze_threshold = 50
autovacuum_vacuum_scale_factor = 0.1
autovacuum_analyze_scale_factor = 0.05
```

### 6.3 Scripts de Limpeza

```sql
-- Limpeza de logs antigos (executar mensalmente)
DELETE FROM audit_log WHERE timestamp < NOW() - INTERVAL '1 year';

-- Reindexação de tabelas grandes (executar semanalmente)
REINDEX TABLE contratacao;
REINDEX TABLE item_contratacao;
```

## 7. Segurança e Controle de Acesso

### 7.1 Roles e Permissões

```sql
-- Criar roles por perfil
CREATE ROLE pncp_readonly;
CREATE ROLE pncp_readwrite;
CREATE ROLE pncp_admin;

-- Permissões para consulta
GRANT SELECT ON ALL TABLES IN SCHEMA public TO pncp_readonly;

-- Permissões para operações
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO pncp_readwrite;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO pncp_readwrite;

-- Permissões administrativas
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pncp_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pncp_admin;
```

### 7.2 Row Level Security (RLS)

```sql
-- Habilitar RLS para controle de acesso por órgão
ALTER TABLE contratacao ENABLE ROW LEVEL SECURITY;

-- Política para usuários verem apenas dados do seu órgão
CREATE POLICY contratacao_orgao_policy ON contratacao
FOR ALL TO pncp_readwrite
USING (orgao_id = current_setting('app.current_orgao_id')::integer);
```

### 7.3 Criptografia de Dados Sensíveis

```sql
-- Extensão para criptografia
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Criptografar campos sensíveis
ALTER TABLE usuario ADD COLUMN dados_pessoais_encrypted BYTEA;

-- Função para criptografar
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(data TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(data, current_setting('app.encryption_key'));
END;
$$ LANGUAGE plpgsql;
```

## 8. Procedures e Funções Especializadas

### 8.1 Função de Sincronização

```sql
CREATE OR REPLACE FUNCTION sync_contratacao_pncp(
    p_numero_controle VARCHAR(50),
    p_dados_json JSONB
) RETURNS BOOLEAN AS $$
DECLARE
    v_contratacao_id INTEGER;
    v_orgao_id INTEGER;
BEGIN
    -- Buscar ou criar órgão
    SELECT id INTO v_orgao_id 
    FROM orgao_entidade 
    WHERE cnpj = p_dados_json->>'orgaoEntidadeCnpj';
    
    IF v_orgao_id IS NULL THEN
        INSERT INTO orgao_entidade (cnpj, razao_social)
        VALUES (
            p_dados_json->>'orgaoEntidadeCnpj',
            p_dados_json->>'orgaoEntidadeRazaoSocial'
        )
        RETURNING id INTO v_orgao_id;
    END IF;
    
    -- Inserir ou atualizar contratação
    INSERT INTO contratacao (
        numero_controle_pncp,
        modalidade_id,
        modalidade_nome,
        objeto_compra,
        orgao_id,
        data_sincronizacao
    )
    VALUES (
        p_numero_controle,
        (p_dados_json->>'modalidadeId')::INTEGER,
        p_dados_json->>'modalidadeNome',
        p_dados_json->>'objetoCompra',
        v_orgao_id,
        NOW()
    )
    ON CONFLICT (numero_controle_pncp) DO UPDATE SET
        modalidade_id = EXCLUDED.modalidade_id,
        modalidade_nome = EXCLUDED.modalidade_nome,
        objeto_compra = EXCLUDED.objeto_compra,
        data_sincronizacao = NOW();
    
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;
```

### 8.2 Função de Auditoria

```sql
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (tabela, registro_id, operacao, dados_anteriores)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', to_jsonb(OLD));
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (tabela, registro_id, operacao, dados_anteriores, dados_novos)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (tabela, registro_id, operacao, dados_novos)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', to_jsonb(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger de auditoria
CREATE TRIGGER contratacao_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON contratacao
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

## 9. Migrations e Versionamento

### 9.1 Estrutura de Migrations (Alembic)

```python
# alembic/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Criar tabelas base
    op.create_table(
        'orgao_entidade',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cnpj', sa.String(14), nullable=False),
        sa.Column('razao_social', sa.String(255), nullable=False),
        # ... outros campos
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices
    op.create_index('idx_orgao_cnpj', 'orgao_entidade', ['cnpj'])

def downgrade():
    op.drop_table('orgao_entidade')
```

### 9.2 Seeds de Dados

```sql
-- Inserir dados iniciais das tabelas de domínio
INSERT INTO tabela_dominio (categoria, codigo, nome, descricao) VALUES
('modalidade', 1, 'Leilão - Eletrônico', 'Modalidade de licitação eletrônica'),
('modalidade', 2, 'Diálogo Competitivo', 'Modalidade de diálogo competitivo'),
('modalidade', 6, 'Pregão - Eletrônico', 'Modalidade de pregão eletrônico'),
('modalidade', 8, 'Dispensa de Licitação', 'Contratação com dispensa de licitação'),
('situacao', 1, 'Divulgada no PNCP', 'Contratação divulgada no portal'),
('situacao', 2, 'Revogada', 'Contratação revogada'),
('situacao', 3, 'Anulada', 'Contratação anulada'),
('amparo_legal', 1, 'Lei 14.133/2021, Art. 28, I', 'Amparo legal específico');
```

## 10. Performance e Otimização

### 10.1 Estratégias de Cache

```sql
-- Materialized Views para consultas frequentes
CREATE MATERIALIZED VIEW mv_contratacoes_resumo AS
SELECT 
    modalidade_id,
    modalidade_nome,
    COUNT(*) as total_contratacoes,
    SUM(valor_total_estimado) as valor_total,
    AVG(valor_total_estimado) as valor_medio
FROM contratacao
WHERE data_publicacao_pncp >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY modalidade_id, modalidade_nome;

-- Índice na materialized view
CREATE INDEX idx_mv_contratacoes_modalidade ON mv_contratacoes_resumo(modalidade_id);

-- Refresh automático
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_contratacoes_resumo;
END;
$$ LANGUAGE plpgsql;
```

### 10.2 Otimização de Consultas

```sql
-- Consulta otimizada para busca de contratações
CREATE OR REPLACE FUNCTION buscar_contratacoes(
    p_termo_busca TEXT DEFAULT NULL,
    p_modalidade_id INTEGER DEFAULT NULL,
    p_data_inicio DATE DEFAULT NULL,
    p_data_fim DATE DEFAULT NULL,
    p_limite INTEGER DEFAULT 50,
    p_offset INTEGER DEFAULT 0
) RETURNS TABLE (
    id INTEGER,
    numero_controle_pncp VARCHAR(50),
    objeto_compra TEXT,
    modalidade_nome VARCHAR(100),
    valor_total_estimado DECIMAL(15,4),
    data_publicacao_pncp DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.numero_controle_pncp,
        c.objeto_compra,
        c.modalidade_nome,
        c.valor_total_estimado,
        c.data_publicacao_pncp
    FROM contratacao c
    WHERE 
        (p_termo_busca IS NULL OR c.objeto_compra ILIKE '%' || p_termo_busca || '%')
        AND (p_modalidade_id IS NULL OR c.modalidade_id = p_modalidade_id)
        AND (p_data_inicio IS NULL OR c.data_publicacao_pncp >= p_data_inicio)
        AND (p_data_fim IS NULL OR c.data_publicacao_pncp <= p_data_fim)
    ORDER BY c.data_publicacao_pncp DESC
    LIMIT p_limite OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;
```

Este plano completo de banco de dados fornece uma base sólida para o sistema PNCP, cobrindo desde a modelagem até a operação em produção, com foco em performance, segurança e manutenibilidade.
