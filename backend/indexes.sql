-- ================================================
-- SEARCB Database Optimized Indexes
-- Performance optimizations for PNCP queries
-- ================================================

SET search_path TO searcb, public;

-- ================================================
-- USUARIO TABLE INDEXES
-- ================================================

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_usuario_username 
    ON usuario(username);

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_usuario_email 
    ON usuario(email);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usuario_orgao_cnpj 
    ON usuario(orgao_cnpj) WHERE orgao_cnpj IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usuario_ativo 
    ON usuario(ativo) WHERE ativo = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usuario_roles 
    ON usuario(is_admin, is_gestor, is_operador) WHERE ativo = true;

-- ================================================
-- LOG_SISTEMA TABLE INDEXES
-- ================================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_sistema_timestamp 
    ON log_sistema(timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_sistema_nivel 
    ON log_sistema(nivel);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_sistema_modulo 
    ON log_sistema(modulo);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_sistema_user_id 
    ON log_sistema(user_id) WHERE user_id IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_sistema_nivel_timestamp 
    ON log_sistema(nivel, timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_sistema_modulo_timestamp 
    ON log_sistema(modulo, timestamp DESC);

-- GIN index for full-text search on mensagem
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_sistema_mensagem_gin 
    ON log_sistema USING GIN(to_tsvector('portuguese', mensagem));

-- JSON index for detalhes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_log_sistema_detalhes_gin 
    ON log_sistema USING GIN(detalhes) WHERE detalhes IS NOT NULL;

-- ================================================
-- CONFIGURACAO_SISTEMA TABLE INDEXES
-- ================================================

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_configuracao_sistema_chave 
    ON configuracao_sistema(chave);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_configuracao_sistema_categoria 
    ON configuracao_sistema(categoria);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_configuracao_sistema_tipo 
    ON configuracao_sistema(tipo);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_configuracao_sistema_editavel 
    ON configuracao_sistema(editavel) WHERE editavel = true;

-- ================================================
-- PCA TABLE INDEXES
-- ================================================

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_pca_id_pncp 
    ON pca(id_pca_pncp) WHERE id_pca_pncp IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pca_ano 
    ON pca(ano_pca);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pca_orgao_cnpj 
    ON pca(orgao_entidade_cnpj) WHERE orgao_entidade_cnpj IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pca_codigo_unidade 
    ON pca(codigo_unidade) WHERE codigo_unidade IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pca_data_publicacao 
    ON pca(data_publicacao_pncp) WHERE data_publicacao_pncp IS NOT NULL;

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pca_ano_orgao 
    ON pca(ano_pca, orgao_entidade_cnpj);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pca_ano_unidade 
    ON pca(ano_pca, codigo_unidade);

-- ================================================
-- ITEM_PCA TABLE INDEXES
-- ================================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_pca_pca_id 
    ON item_pca(pca_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_pca_numero_item 
    ON item_pca(numero_item);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_pca_classificacao_superior 
    ON item_pca(classificacao_superior_codigo) WHERE classificacao_superior_codigo IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_pca_pdm_codigo 
    ON item_pca(pdm_codigo) WHERE pdm_codigo IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_pca_grupo_contratacao 
    ON item_pca(grupo_contratacao_codigo) WHERE grupo_contratacao_codigo IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_pca_valor_total 
    ON item_pca(valor_total) WHERE valor_total IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_pca_data_desejada 
    ON item_pca(data_desejada) WHERE data_desejada IS NOT NULL;

-- GIN index for full-text search on descricao_item
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_pca_descricao_gin 
    ON item_pca USING GIN(to_tsvector('portuguese', descricao_item));

-- Composite indexes for common PCA queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_pca_pca_classificacao 
    ON item_pca(pca_id, classificacao_superior_codigo);

-- ================================================
-- CONTRATACAO TABLE INDEXES
-- ================================================

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_numero_controle_pncp 
    ON contratacao(numero_controle_pncp);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_ano_compra 
    ON contratacao(ano_compra);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_modalidade_id 
    ON contratacao(modalidade_id) WHERE modalidade_id IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_situacao_compra_id 
    ON contratacao(situacao_compra_id) WHERE situacao_compra_id IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_data_publicacao_pncp 
    ON contratacao(data_publicacao_pncp) WHERE data_publicacao_pncp IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_data_encerramento_proposta 
    ON contratacao(data_encerramento_proposta) WHERE data_encerramento_proposta IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_orgao_cnpj 
    ON contratacao(orgao_entidade_cnpj) WHERE orgao_entidade_cnpj IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_unidade_uf 
    ON contratacao(unidade_orgao_uf_sigla) WHERE unidade_orgao_uf_sigla IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_unidade_codigo_ibge 
    ON contratacao(unidade_orgao_codigo_ibge) WHERE unidade_orgao_codigo_ibge IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_valor_estimado 
    ON contratacao(valor_total_estimado) WHERE valor_total_estimado IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_srp 
    ON contratacao(srp) WHERE srp = true;

-- GIN index for full-text search on objeto_compra
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_objeto_gin 
    ON contratacao USING GIN(to_tsvector('portuguese', objeto_compra));

-- Composite indexes for common PNCP queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_data_modalidade 
    ON contratacao(data_publicacao_pncp, modalidade_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_uf_modalidade 
    ON contratacao(unidade_orgao_uf_sigla, modalidade_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_orgao_modalidade 
    ON contratacao(orgao_entidade_cnpj, modalidade_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_situacao_modalidade 
    ON contratacao(situacao_compra_id, modalidade_id);

-- Index for proposals still open
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contratacao_propostas_abertas 
    ON contratacao(data_encerramento_proposta, modalidade_id) 
    WHERE data_encerramento_proposta > CURRENT_TIMESTAMP;

-- ================================================
-- ITEM_CONTRATACAO TABLE INDEXES
-- ================================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_contratacao_contratacao_id 
    ON item_contratacao(contratacao_id, ano_compra);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_contratacao_numero_item 
    ON item_contratacao(numero_item);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_contratacao_situacao_item_id 
    ON item_contratacao(situacao_item_id) WHERE situacao_item_id IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_contratacao_tipo_beneficio_id 
    ON item_contratacao(tipo_beneficio_id) WHERE tipo_beneficio_id IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_contratacao_valor_total 
    ON item_contratacao(valor_total) WHERE valor_total IS NOT NULL;

-- GIN index for full-text search on descricao_item
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_contratacao_descricao_gin 
    ON item_contratacao USING GIN(to_tsvector('portuguese', descricao_item));

-- ================================================
-- ATA_REGISTRO_PRECO TABLE INDEXES
-- ================================================

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_ata_numero_controle_pncp_ata 
    ON ata_registro_preco(numero_controle_pncp_ata) WHERE numero_controle_pncp_ata IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ata_numero_controle_pncp_compra 
    ON ata_registro_preco(numero_controle_pncp_compra) WHERE numero_controle_pncp_compra IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ata_ano_ata 
    ON ata_registro_preco(ano_ata) WHERE ano_ata IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ata_vigencia_inicio 
    ON ata_registro_preco(vigencia_inicio) WHERE vigencia_inicio IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ata_vigencia_fim 
    ON ata_registro_preco(vigencia_fim) WHERE vigencia_fim IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ata_cnpj_orgao 
    ON ata_registro_preco(cnpj_orgao) WHERE cnpj_orgao IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ata_cancelado 
    ON ata_registro_preco(cancelado);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ata_data_publicacao_pncp 
    ON ata_registro_preco(data_publicacao_pncp) WHERE data_publicacao_pncp IS NOT NULL;

-- GIN index for full-text search on objeto_contratacao
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ata_objeto_gin 
    ON ata_registro_preco USING GIN(to_tsvector('portuguese', objeto_contratacao));

-- Composite indexes for vigência queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ata_vigencia_range 
    ON ata_registro_preco(vigencia_inicio, vigencia_fim) 
    WHERE cancelado = false;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ata_orgao_vigencia 
    ON ata_registro_preco(cnpj_orgao, vigencia_inicio, vigencia_fim) 
    WHERE cancelado = false;

-- ================================================
-- CONTRATO TABLE INDEXES
-- ================================================

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_numero_controle_pncp 
    ON contrato(numero_controle_pncp) WHERE numero_controle_pncp IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_numero_controle_pncp_compra 
    ON contrato(numero_controle_pncp_compra) WHERE numero_controle_pncp_compra IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_ano_contrato 
    ON contrato(ano_contrato) WHERE ano_contrato IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_tipo_contrato_id 
    ON contrato(tipo_contrato_id) WHERE tipo_contrato_id IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_categoria_processo_id 
    ON contrato(categoria_processo_id) WHERE categoria_processo_id IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_orgao_cnpj 
    ON contrato(orgao_entidade_cnpj) WHERE orgao_entidade_cnpj IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_data_vigencia_inicio 
    ON contrato(data_vigencia_inicio) WHERE data_vigencia_inicio IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_data_vigencia_fim 
    ON contrato(data_vigencia_fim) WHERE data_vigencia_fim IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_data_publicacao_pncp 
    ON contrato(data_publicacao_pncp) WHERE data_publicacao_pncp IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_ni_fornecedor 
    ON contrato(ni_fornecedor) WHERE ni_fornecedor IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_valor_global 
    ON contrato(valor_global) WHERE valor_global IS NOT NULL;

-- GIN index for full-text search on objeto_contrato
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_objeto_gin 
    ON contrato USING GIN(to_tsvector('portuguese', objeto_contrato));

-- Composite indexes for common contract queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_vigencia_range 
    ON contrato(data_vigencia_inicio, data_vigencia_fim);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_orgao_vigencia 
    ON contrato(orgao_entidade_cnpj, data_vigencia_inicio, data_vigencia_fim);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_tipo_vigencia 
    ON contrato(tipo_contrato_id, data_vigencia_inicio, data_vigencia_fim);

-- Contracts expiring soon
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contrato_vencendo 
    ON contrato(data_vigencia_fim) 
    WHERE data_vigencia_fim BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days';

-- ================================================
-- DOMAIN TABLES INDEXES
-- ================================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_modalidade_contratacao_ativo 
    ON modalidade_contratacao(ativo) WHERE ativo = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_situacao_contratacao_ativo 
    ON situacao_contratacao(ativo) WHERE ativo = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_modo_disputa_ativo 
    ON modo_disputa(ativo) WHERE ativo = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_amparo_legal_ativo 
    ON amparo_legal(ativo) WHERE ativo = true;

-- ================================================
-- AUDIT AND MONITORING INDEXES
-- ================================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_table_name 
    ON audit.audit_log(table_name);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_operation 
    ON audit.audit_log(operation);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_user_name 
    ON audit.audit_log(user_name);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_changed_at 
    ON audit.audit_log(changed_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_database_stats_table_name 
    ON monitoring.database_stats(table_name);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_database_stats_collected_at 
    ON monitoring.database_stats(collected_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_query_performance_query_hash 
    ON monitoring.query_performance(query_hash);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_query_performance_collected_at 
    ON monitoring.query_performance(collected_at DESC);

-- ================================================
-- STATISTICS UPDATES
-- ================================================

-- Update table statistics for better query planning
ANALYZE usuario;
ANALYZE log_sistema;
ANALYZE configuracao_sistema;
ANALYZE pca;
ANALYZE item_pca;
ANALYZE contratacao;
ANALYZE item_contratacao;
ANALYZE ata_registro_preco;
ANALYZE contrato;
ANALYZE modalidade_contratacao;
ANALYZE situacao_contratacao;
ANALYZE modo_disputa;
ANALYZE amparo_legal;

-- Set custom statistics targets for important columns
ALTER TABLE contratacao ALTER COLUMN modalidade_id SET STATISTICS 1000;
ALTER TABLE contratacao ALTER COLUMN situacao_compra_id SET STATISTICS 1000;
ALTER TABLE contratacao ALTER COLUMN orgao_entidade_cnpj SET STATISTICS 1000;
ALTER TABLE contratacao ALTER COLUMN unidade_orgao_uf_sigla SET STATISTICS 1000;
ALTER TABLE contratacao ALTER COLUMN data_publicacao_pncp SET STATISTICS 1000;

ALTER TABLE item_pca ALTER COLUMN classificacao_superior_codigo SET STATISTICS 1000;
ALTER TABLE item_pca ALTER COLUMN pdm_codigo SET STATISTICS 1000;

ALTER TABLE contrato ALTER COLUMN tipo_contrato_id SET STATISTICS 1000;
ALTER TABLE contrato ALTER COLUMN categoria_processo_id SET STATISTICS 1000;
ALTER TABLE contrato ALTER COLUMN orgao_entidade_cnpj SET STATISTICS 1000;

-- Final analyze to update statistics
ANALYZE;

-- Show index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE schemaname = 'searcb'
ORDER BY idx_tup_read DESC;

-- (já cobre: índices para performance, busca textual, índices compostos, estatísticas)
