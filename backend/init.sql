-- ================================================
-- SEARCB Database Initialization Script
-- Sistema de Gestão Pública - PNCP Integration
-- PostgreSQL 15 Compatible
-- ================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS searcb;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Set search path
SET search_path TO searcb, public;

-- ================================================
-- DOMAIN TYPES
-- ================================================

CREATE DOMAIN email AS VARCHAR(255) CHECK (VALUE ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
CREATE DOMAIN cnpj AS VARCHAR(14) CHECK (VALUE ~ '^[0-9]{14}$');
CREATE DOMAIN cpf AS VARCHAR(11) CHECK (VALUE ~ '^[0-9]{11}$');
CREATE DOMAIN uf_sigla AS VARCHAR(2) CHECK (VALUE ~ '^[A-Z]{2}$');

-- ================================================
-- AUDIT TRIGGER FUNCTION
-- ================================================

CREATE OR REPLACE FUNCTION audit.audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit.audit_log (
            schema_name, table_name, operation, user_name,
            new_data, changed_at
        ) VALUES (
            TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP, current_user,
            row_to_json(NEW), current_timestamp
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit.audit_log (
            schema_name, table_name, operation, user_name,
            old_data, new_data, changed_at
        ) VALUES (
            TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP, current_user,
            row_to_json(OLD), row_to_json(NEW), current_timestamp
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit.audit_log (
            schema_name, table_name, operation, user_name,
            old_data, changed_at
        ) VALUES (
            TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP, current_user,
            row_to_json(OLD), current_timestamp
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- AUDIT LOG TABLE
-- ================================================

CREATE TABLE audit.audit_log (
    id BIGSERIAL PRIMARY KEY,
    schema_name VARCHAR(64) NOT NULL,
    table_name VARCHAR(64) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    user_name VARCHAR(64) NOT NULL,
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp
);

-- ================================================
-- CORE TABLES
-- ================================================

-- Usuarios table
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email email UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    nome_completo VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    cargo VARCHAR(100),
    orgao_cnpj cnpj,
    orgao_nome VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE,
    is_gestor BOOLEAN DEFAULT FALSE,
    is_operador BOOLEAN DEFAULT TRUE,
    ativo BOOLEAN DEFAULT TRUE,
    ultimo_login TIMESTAMP WITH TIME ZONE,
    configuracoes JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp
);

-- Log Sistema table
CREATE TABLE log_sistema (
    id BIGSERIAL PRIMARY KEY,
    nivel VARCHAR(10) NOT NULL CHECK (nivel IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    modulo VARCHAR(100) NOT NULL,
    mensagem TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    user_id INTEGER REFERENCES usuario(id),
    request_id VARCHAR(50),
    detalhes JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp
) PARTITION BY RANGE (timestamp);

-- Configuracao Sistema table
CREATE TABLE configuracao_sistema (
    id SERIAL PRIMARY KEY,
    chave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT NOT NULL,
    descricao TEXT,
    categoria VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('string', 'integer', 'boolean', 'json', 'decimal')),
    editavel BOOLEAN DEFAULT TRUE,
    valor_padrao TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp
);

-- PCA table
CREATE TABLE pca (
    id SERIAL PRIMARY KEY,
    id_pca_pncp VARCHAR(50) UNIQUE,
    ano_pca INTEGER NOT NULL CHECK (ano_pca >= 2000 AND ano_pca <= 2050),
    data_publicacao_pncp DATE,
    orgao_entidade_cnpj cnpj,
    orgao_entidade_razao_social VARCHAR(255),
    codigo_unidade VARCHAR(20),
    nome_unidade VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp
);

-- Item PCA table
CREATE TABLE item_pca (
    id SERIAL PRIMARY KEY,
    pca_id INTEGER NOT NULL REFERENCES pca(id) ON DELETE CASCADE,
    numero_item INTEGER NOT NULL,
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
    data_atualizacao DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    UNIQUE(pca_id, numero_item)
);

-- Contratacao table - partitioned by year
CREATE TABLE contratacao (
    id SERIAL,
    numero_controle_pncp VARCHAR(50) UNIQUE NOT NULL,
    numero_compra VARCHAR(50),
    ano_compra INTEGER NOT NULL,
    processo VARCHAR(50),
    tipo_instrumento_convocatorio_id INTEGER,
    tipo_instrumento_convocatorio_nome VARCHAR(100),
    modalidade_id INTEGER,
    modalidade_nome VARCHAR(100),
    modo_disputa_id INTEGER,
    modo_disputa_nome VARCHAR(100),
    situacao_compra_id INTEGER,
    situacao_compra_nome VARCHAR(100),
    objeto_compra TEXT,
    informacao_complementar TEXT,
    srp BOOLEAN DEFAULT FALSE,
    amparo_legal_codigo INTEGER,
    amparo_legal_nome VARCHAR(255),
    amparo_legal_descricao TEXT,
    valor_total_estimado DECIMAL(15,4),
    valor_total_homologado DECIMAL(15,4),
    data_abertura_proposta TIMESTAMP WITH TIME ZONE,
    data_encerramento_proposta TIMESTAMP WITH TIME ZONE,
    data_publicacao_pncp DATE,
    data_inclusao DATE,
    data_atualizacao DATE,
    sequencial_compra INTEGER,
    orgao_entidade_cnpj cnpj,
    orgao_entidade_razao_social VARCHAR(255),
    orgao_entidade_poder_id VARCHAR(1),
    orgao_entidade_esfera_id VARCHAR(1),
    unidade_orgao_codigo VARCHAR(20),
    unidade_orgao_nome VARCHAR(255),
    unidade_orgao_codigo_ibge INTEGER,
    unidade_orgao_municipio VARCHAR(100),
    unidade_orgao_uf_sigla uf_sigla,
    unidade_orgao_uf_nome VARCHAR(50),
    orgao_subrogado_cnpj cnpj,
    orgao_subrogado_razao_social VARCHAR(255),
    orgao_subrogado_poder_id VARCHAR(1),
    orgao_subrogado_esfera_id VARCHAR(1),
    unidade_subrogada_codigo VARCHAR(20),
    unidade_subrogada_nome VARCHAR(255),
    unidade_subrogada_codigo_ibge INTEGER,
    unidade_subrogada_municipio VARCHAR(100),
    unidade_subrogada_uf_sigla uf_sigla,
    unidade_subrogada_uf_nome VARCHAR(50),
    usuario_nome VARCHAR(255),
    link_sistema_origem VARCHAR(500),
    justificativa_presencial TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    PRIMARY KEY (id, ano_compra)
) PARTITION BY RANGE (ano_compra);

-- Item Contratacao table
CREATE TABLE item_contratacao (
    id SERIAL PRIMARY KEY,
    contratacao_id INTEGER NOT NULL,
    ano_compra INTEGER NOT NULL,
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    FOREIGN KEY (contratacao_id, ano_compra) REFERENCES contratacao(id, ano_compra) ON DELETE CASCADE
);

-- Ata Registro Preco table
CREATE TABLE ata_registro_preco (
    id SERIAL PRIMARY KEY,
    numero_controle_pncp_ata VARCHAR(50) UNIQUE,
    numero_controle_pncp_compra VARCHAR(50),
    numero_ata_registro_preco VARCHAR(50),
    ano_ata INTEGER,
    data_assinatura DATE,
    vigencia_inicio DATE,
    vigencia_fim DATE,
    data_cancelamento DATE,
    cancelado BOOLEAN DEFAULT FALSE,
    data_publicacao_pncp DATE,
    data_inclusao DATE,
    data_atualizacao DATE,
    objeto_contratacao TEXT,
    cnpj_orgao cnpj,
    nome_orgao VARCHAR(255),
    codigo_unidade_orgao VARCHAR(20),
    nome_unidade_orgao VARCHAR(255),
    cnpj_orgao_subrogado cnpj,
    nome_orgao_subrogado VARCHAR(255),
    codigo_unidade_orgao_subrogado VARCHAR(20),
    nome_unidade_orgao_subrogado VARCHAR(255),
    usuario VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp
);

-- Contrato table
CREATE TABLE contrato (
    id SERIAL PRIMARY KEY,
    numero_controle_pncp VARCHAR(50) UNIQUE,
    numero_controle_pncp_compra VARCHAR(50),
    numero_contrato_empenho VARCHAR(50),
    ano_contrato INTEGER,
    sequencial_contrato INTEGER,
    processo VARCHAR(50),
    tipo_contrato_id INTEGER,
    tipo_contrato_nome VARCHAR(100),
    categoria_processo_id INTEGER,
    categoria_processo_nome VARCHAR(100),
    receita BOOLEAN DEFAULT FALSE,
    objeto_contrato TEXT,
    informacao_complementar TEXT,
    orgao_entidade_cnpj cnpj,
    orgao_entidade_razao_social VARCHAR(255),
    orgao_entidade_poder_id VARCHAR(1),
    orgao_entidade_esfera_id VARCHAR(1),
    unidade_orgao_codigo VARCHAR(20),
    unidade_orgao_nome VARCHAR(255),
    unidade_orgao_codigo_ibge INTEGER,
    unidade_orgao_municipio VARCHAR(100),
    unidade_orgao_uf_sigla uf_sigla,
    unidade_orgao_uf_nome VARCHAR(50),
    orgao_subrogado_cnpj cnpj,
    orgao_subrogado_razao_social VARCHAR(255),
    orgao_subrogado_poder_id VARCHAR(1),
    orgao_subrogado_esfera_id VARCHAR(1),
    unidade_subrogada_codigo VARCHAR(20),
    unidade_subrogada_nome VARCHAR(255),
    unidade_subrogada_codigo_ibge INTEGER,
    unidade_subrogada_municipio VARCHAR(100),
    unidade_subrogada_uf_sigla uf_sigla,
    unidade_subrogada_uf_nome VARCHAR(50),
    tipo_pessoa VARCHAR(2),
    ni_fornecedor VARCHAR(30),
    nome_razao_social_fornecedor VARCHAR(100),
    tipo_pessoa_subcontratada VARCHAR(2),
    ni_fornecedor_subcontratado VARCHAR(30),
    nome_fornecedor_subcontratado VARCHAR(100),
    valor_inicial DECIMAL(15,4),
    numero_parcelas INTEGER,
    valor_parcela DECIMAL(15,4),
    valor_global DECIMAL(15,4),
    valor_acumulado DECIMAL(15,4),
    data_assinatura DATE,
    data_vigencia_inicio DATE,
    data_vigencia_fim DATE,
    data_publicacao_pncp TIMESTAMP WITH TIME ZONE,
    data_atualizacao TIMESTAMP WITH TIME ZONE,
    numero_retificacao INTEGER,
    usuario_nome VARCHAR(255),
    identificador_cipi VARCHAR(100),
    url_cipi VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp
);

-- ================================================
-- PARTITIONS FOR LOG_SISTEMA (Monthly partitions)
-- ================================================

-- Create partitions for log_sistema (current year + next year)
DO $$
DECLARE
    start_date DATE;
    end_date DATE;
    partition_name TEXT;
    year_val INTEGER;
    month_val INTEGER;
BEGIN
    -- Create partitions for current year and next year
    FOR year_val IN SELECT generate_series(EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER, 
                                          EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER + 1) LOOP
        FOR month_val IN 1..12 LOOP
            start_date := DATE(year_val || '-' || LPAD(month_val::TEXT, 2, '0') || '-01');
            end_date := start_date + INTERVAL '1 month';
            partition_name := 'log_sistema_' || year_val || '_' || LPAD(month_val::TEXT, 2, '0');
            
            EXECUTE FORMAT('CREATE TABLE %I PARTITION OF log_sistema 
                           FOR VALUES FROM (%L) TO (%L)',
                          partition_name, start_date, end_date);
        END LOOP;
    END LOOP;
END $$;

-- ================================================
-- PARTITIONS FOR CONTRATACAO (Yearly partitions)
-- ================================================

-- Create partitions for contratacao (2020-2030)
DO $$
DECLARE
    year_val INTEGER;
    partition_name TEXT;
BEGIN
    FOR year_val IN 2020..2030 LOOP
        partition_name := 'contratacao_' || year_val;
        EXECUTE FORMAT('CREATE TABLE %I PARTITION OF contratacao 
                       FOR VALUES FROM (%L) TO (%L)',
                      partition_name, year_val, year_val + 1);
    END LOOP;
END $$;

-- ================================================
-- DOMAIN TABLES
-- ================================================

-- Modalidade Contratacao
CREATE TABLE modalidade_contratacao (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE
);

-- Situacao Contratacao
CREATE TABLE situacao_contratacao (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE
);

-- Modo Disputa
CREATE TABLE modo_disputa (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE
);

-- Amparo Legal
CREATE TABLE amparo_legal (
    codigo INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    artigo VARCHAR(50),
    inciso VARCHAR(10),
    ativo BOOLEAN DEFAULT TRUE
);

-- ================================================
-- MONITORING TABLES
-- ================================================

CREATE TABLE monitoring.database_stats (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(64) NOT NULL,
    total_rows BIGINT,
    total_size_bytes BIGINT,
    index_size_bytes BIGINT,
    last_vacuum TIMESTAMP WITH TIME ZONE,
    last_analyze TIMESTAMP WITH TIME ZONE,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp
);

CREATE TABLE monitoring.query_performance (
    id SERIAL PRIMARY KEY,
    query_hash CHAR(32) NOT NULL,
    query_text TEXT,
    total_calls BIGINT,
    total_time_ms DOUBLE PRECISION,
    mean_time_ms DOUBLE PRECISION,
    min_time_ms DOUBLE PRECISION,
    max_time_ms DOUBLE PRECISION,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp
);

-- ================================================
-- UPDATED_AT TRIGGER FUNCTION
-- ================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = current_timestamp;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- CREATE TRIGGERS
-- ================================================

-- Updated_at triggers
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN SELECT tablename FROM pg_tables 
             WHERE schemaname = 'searcb' 
             AND tablename NOT LIKE '%_prt_%'  -- Skip partition tables
    LOOP
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_schema = 'searcb' 
                  AND table_name = t 
                  AND column_name = 'updated_at') THEN
            EXECUTE FORMAT('CREATE TRIGGER trigger_update_updated_at_%I
                           BEFORE UPDATE ON %I
                           FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', t, t);
        END IF;
    END LOOP;
END $$;

-- Audit triggers for sensitive tables
CREATE TRIGGER usuario_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON usuario
    FOR EACH ROW EXECUTE FUNCTION audit.audit_trigger_function();

CREATE TRIGGER configuracao_sistema_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON configuracao_sistema
    FOR EACH ROW EXECUTE FUNCTION audit.audit_trigger_function();

-- ================================================
-- SECURITY SETUP
-- ================================================

-- Create roles
CREATE ROLE searcb_admin;
CREATE ROLE searcb_gestor;
CREATE ROLE searcb_operador;
CREATE ROLE searcb_readonly;

-- Grant permissions
GRANT ALL ON SCHEMA searcb TO searcb_admin;
GRANT ALL ON ALL TABLES IN SCHEMA searcb TO searcb_admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA searcb TO searcb_admin;

GRANT USAGE ON SCHEMA searcb TO searcb_gestor;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA searcb TO searcb_gestor;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA searcb TO searcb_gestor;

GRANT USAGE ON SCHEMA searcb TO searcb_operador;
GRANT SELECT ON ALL TABLES IN SCHEMA searcb TO searcb_operador;
GRANT INSERT, UPDATE ON pca, item_pca TO searcb_operador;

GRANT USAGE ON SCHEMA searcb TO searcb_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA searcb TO searcb_readonly;

-- Row Level Security
ALTER TABLE usuario ENABLE ROW LEVEL SECURITY;

CREATE POLICY usuario_own_data ON usuario
    FOR ALL TO searcb_operador
    USING (username = current_user);

CREATE POLICY usuario_all_access ON usuario
    FOR ALL TO searcb_admin, searcb_gestor
    USING (true);

-- ================================================
-- PERFORMANCE CONFIGURATIONS
-- ================================================

-- Analyze all tables
ANALYZE;

-- Update statistics
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats 
WHERE schemaname = 'searcb'
ORDER BY schemaname, tablename, attname;

COMMIT;

-- (já cobre: schemas, tabelas, domínios, triggers, roles, RLS, particionamento, grants)
