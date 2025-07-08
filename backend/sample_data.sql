-- ================================================
-- SEARCB Sample Data
-- Test data for development and demonstration
-- ================================================

SET search_path TO searcb, public;

-- ================================================
-- SAMPLE USERS
-- ================================================

-- Create sample users with different roles
INSERT INTO usuario (
    username, email, senha_hash, nome_completo, telefone, cargo,
    orgao_cnpj, orgao_nome, is_admin, is_gestor, is_operador,
    ativo, created_at, updated_at
) VALUES 
-- Admin user
('admin', 'admin@searcb.gov.br', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/WQr0Z7.vL/GxH1.L6', 
 'Administrador do Sistema', '(61) 99999-0001', 'Administrador de Sistema',
 '00000000000191', 'Ministério da Economia', TRUE, TRUE, TRUE, TRUE,
 current_timestamp, current_timestamp),

-- Gestor user  
('gestor.compras', 'gestor@searcb.gov.br', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/WQr0Z7.vL/GxH1.L6',
 'João Silva Santos', '(61) 99999-0002', 'Gestor de Compras',
 '00000000000191', 'Ministério da Economia', FALSE, TRUE, TRUE, TRUE,
 current_timestamp, current_timestamp),

-- Operador user
('operador.sp', 'operador@searcb.gov.br', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/WQr0Z7.vL/GxH1.L6',
 'Maria Oliveira Costa', '(11) 99999-0003', 'Operador de Compras',
 '46522729000118', 'Prefeitura de São Paulo', FALSE, FALSE, TRUE, TRUE,
 current_timestamp, current_timestamp),

-- Regular user
('user.rj', 'user@searcb.gov.br', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/WQr0Z7.vL/GxH1.L6',
 'Carlos Pereira Lima', '(21) 99999-0004', 'Analista de Compras',
 '29979036000140', 'Estado do Rio de Janeiro', FALSE, FALSE, TRUE, TRUE,
 current_timestamp, current_timestamp);

-- ================================================
-- SYSTEM CONFIGURATIONS
-- ================================================

INSERT INTO configuracao_sistema (
    chave, valor, descricao, categoria, tipo, editavel, valor_padrao,
    created_at, updated_at
) VALUES 
('pncp_api_url', 'https://pncp.gov.br/api/consulta', 'URL base da API do PNCP', 'integracao', 'string', TRUE, 'https://pncp.gov.br/api/consulta', current_timestamp, current_timestamp),
('pncp_timeout', '30', 'Timeout para requisições PNCP (segundos)', 'integracao', 'integer', TRUE, '30', current_timestamp, current_timestamp),
('max_page_size', '500', 'Tamanho máximo de página para consultas', 'api', 'integer', TRUE, '500', current_timestamp, current_timestamp),
('default_page_size', '50', 'Tamanho padrão de página', 'api', 'integer', TRUE, '50', current_timestamp, current_timestamp),
('cache_ttl', '3600', 'Tempo de vida do cache (segundos)', 'cache', 'integer', TRUE, '3600', current_timestamp, current_timestamp),
('rate_limit_requests', '100', 'Limite de requisições por minuto', 'seguranca', 'integer', TRUE, '100', current_timestamp, current_timestamp),
('email_notifications', 'true', 'Habilitar notificações por email', 'notificacoes', 'boolean', TRUE, 'true', current_timestamp, current_timestamp),
('sync_interval', '86400', 'Intervalo de sincronização automática (segundos)', 'integracao', 'integer', TRUE, '86400', current_timestamp, current_timestamp),
('log_level', 'INFO', 'Nível de log do sistema', 'sistema', 'string', TRUE, 'INFO', current_timestamp, current_timestamp),
('maintenance_mode', 'false', 'Modo de manutenção ativo', 'sistema', 'boolean', TRUE, 'false', current_timestamp, current_timestamp);

-- ================================================
-- DOMAIN DATA - MODALIDADES
-- ================================================

INSERT INTO modalidade_contratacao (id, nome, descricao, ativo) VALUES 
(1, 'Leilão - Eletrônico', 'Leilão realizado por meio eletrônico', TRUE),
(2, 'Diálogo Competitivo', 'Procedimento de contratação em que participam fornecedores previamente selecionados', TRUE),
(3, 'Concurso', 'Modalidade de licitação para escolha de trabalho técnico, científico ou artístico', TRUE),
(4, 'Concorrência - Eletrônica', 'Concorrência realizada por meio eletrônico', TRUE),
(5, 'Concorrência - Presencial', 'Concorrência realizada presencialmente', TRUE),
(6, 'Pregão - Eletrônico', 'Pregão realizado por meio eletrônico', TRUE),
(7, 'Pregão - Presencial', 'Pregão realizado presencialmente', TRUE),
(8, 'Dispensa de Licitação', 'Contratação direta por dispensa de licitação', TRUE),
(9, 'Inexigibilidade', 'Contratação direta por inexigibilidade de licitação', TRUE),
(10, 'Manifestação de Interesse', 'Procedimento para manifestação de interesse do setor privado', TRUE),
(11, 'Pré-qualificação', 'Procedimento para pré-qualificação permanente de fornecedores', TRUE),
(12, 'Credenciamento', 'Procedimento para credenciamento de interessados', TRUE),
(13, 'Leilão - Presencial', 'Leilão realizado presencialmente', TRUE);

-- ================================================
-- DOMAIN DATA - SITUAÇÕES
-- ================================================

INSERT INTO situacao_contratacao (id, nome, descricao, ativo) VALUES 
(1, 'Divulgada no PNCP', 'Contratação divulgada no Portal Nacional de Contratações Públicas', TRUE),
(2, 'Revogada', 'Contratação revogada por motivo de interesse público', TRUE),
(3, 'Anulada', 'Contratação anulada por vício de legalidade', TRUE),
(4, 'Suspensa', 'Contratação suspensa temporariamente', TRUE);

-- ================================================
-- DOMAIN DATA - MODO DISPUTA
-- ================================================

INSERT INTO modo_disputa (id, nome, descricao, ativo) VALUES 
(1, 'Aberto', 'Disputa aberta entre os participantes', TRUE),
(2, 'Fechado', 'Disputa com propostas fechadas', TRUE),
(3, 'Aberto e Fechado', 'Combinação de disputa aberta e fechada', TRUE),
(4, 'Dispensa com Disputa', 'Dispensa de licitação com disputa entre fornecedores', TRUE),
(5, 'Não se Aplica', 'Não se aplica modo de disputa', TRUE),
(6, 'Fechado e Aberto', 'Primeiro fechado, depois aberto', TRUE);

-- ================================================
-- DOMAIN DATA - AMPARO LEGAL
-- ================================================

INSERT INTO amparo_legal (codigo, nome, descricao, artigo, inciso, ativo) VALUES 
(1, 'Lei 14.133/2021, Art. 75, I', 'Dispensa para valores até R$ 54.000,00 (obras e serviços de engenharia)', 'Art. 75', 'I', TRUE),
(2, 'Lei 14.133/2021, Art. 75, II', 'Dispensa para valores até R$ 17.600,00 (demais bens e serviços)', 'Art. 75', 'II', TRUE),
(3, 'Lei 14.133/2021, Art. 75, III', 'Guerra ou grave perturbação da ordem', 'Art. 75', 'III', TRUE),
(4, 'Lei 14.133/2021, Art. 75, IV', 'Emergência ou calamidade pública', 'Art. 75', 'IV', TRUE),
(5, 'Lei 14.133/2021, Art. 75, V', 'Não acudirem interessados à licitação anterior', 'Art. 75', 'V', TRUE),
(6, 'Lei 14.133/2021, Art. 74, I', 'Fornecedor exclusivo', 'Art. 74', 'I', TRUE),
(7, 'Lei 14.133/2021, Art. 74, II', 'Serviços técnicos especializados', 'Art. 74', 'II', TRUE),
(8, 'Lei 14.133/2021, Art. 74, III, a', 'Profissional do setor artístico', 'Art. 74', 'III, a', TRUE);

-- ================================================
-- SAMPLE PCA DATA
-- ================================================

-- Insert sample PCA
INSERT INTO pca (
    id_pca_pncp, ano_pca, data_publicacao_pncp,
    orgao_entidade_cnpj, orgao_entidade_razao_social,
    codigo_unidade, nome_unidade,
    created_at, updated_at
) VALUES 
('PCA-2024-001', 2024, '2024-01-15',
 '00000000000191', 'Ministério da Economia',
 '160012', 'Secretaria de Gestão',
 current_timestamp, current_timestamp),

('PCA-2024-002', 2024, '2024-01-20',
 '46522729000118', 'Prefeitura Municipal de São Paulo',
 '010001', 'Secretaria de Administração',
 current_timestamp, current_timestamp);

-- Insert sample PCA items
INSERT INTO item_pca (
    pca_id, numero_item, categoria_item_pca_nome,
    classificacao_catalogo_id, nome_classificacao_catalogo,
    classificacao_superior_codigo, classificacao_superior_nome,
    pdm_codigo, pdm_descricao, codigo_item, descricao_item,
    unidade_fornecimento, quantidade_estimada, valor_unitario,
    valor_total, valor_orcamento_exercicio, data_desejada,
    unidade_requisitante, grupo_contratacao_codigo,
    grupo_contratacao_nome, data_inclusao, data_atualizacao,
    created_at, updated_at
) VALUES 
-- Items for PCA 1
(1, 1, 'Material', 'MAT001', 'Material de Escritório',
 '010101', 'Papel e Papelão', 'PDM001', 'Papel A4 75g/m²',
 'ITEM001', 'Papel sulfite A4 75g/m² branco, pacote com 500 folhas',
 'RESMA', 1000.00, 15.50, 15500.00, 15500.00, '2024-03-01',
 'Secretaria de Gestão', 'GRP001', 'Material de Consumo',
 '2024-01-15', '2024-01-15', current_timestamp, current_timestamp),

(1, 2, 'Serviço', 'SRV001', 'Serviços de Limpeza',
 '020201', 'Serviços Gerais', 'PDM002', 'Limpeza Predial',
 'ITEM002', 'Serviços de limpeza e conservação predial',
 'MÊS', 12.00, 25000.00, 300000.00, 300000.00, '2024-02-01',
 'Secretaria de Gestão', 'GRP002', 'Serviços Terceirizados',
 '2024-01-15', '2024-01-15', current_timestamp, current_timestamp),

-- Items for PCA 2
(2, 1, 'Material', 'MAT002', 'Material de Informática',
 '030301', 'Equipamentos de Informática', 'PDM003', 'Computadores',
 'ITEM003', 'Microcomputador desktop completo com monitor',
 'UNIDADE', 50.00, 3500.00, 175000.00, 175000.00, '2024-04-01',
 'Secretaria de Administração', 'GRP003', 'Equipamentos',
 '2024-01-20', '2024-01-20', current_timestamp, current_timestamp);

-- ================================================
-- SAMPLE CONTRATACAO DATA
-- ================================================

-- Insert sample contratações
INSERT INTO contratacao (
    numero_controle_pncp, numero_compra, ano_compra, processo,
    tipo_instrumento_convocatorio_id, tipo_instrumento_convocatorio_nome,
    modalidade_id, modalidade_nome, modo_disputa_id, modo_disputa_nome,
    situacao_compra_id, situacao_compra_nome, objeto_compra,
    informacao_complementar, srp, amparo_legal_codigo, amparo_legal_nome,
    amparo_legal_descricao, valor_total_estimado, valor_total_homologado,
    data_abertura_proposta, data_encerramento_proposta, data_publicacao_pncp,
    data_inclusao, data_atualizacao, sequencial_compra,
    orgao_entidade_cnpj, orgao_entidade_razao_social,
    orgao_entidade_poder_id, orgao_entidade_esfera_id,
    unidade_orgao_codigo, unidade_orgao_nome, unidade_orgao_codigo_ibge,
    unidade_orgao_municipio, unidade_orgao_uf_sigla, unidade_orgao_uf_nome,
    usuario_nome, link_sistema_origem,
    created_at, updated_at
) VALUES 
-- Pregão Eletrônico para Material de Escritório
('CNTP-2024-001', 'PE-001/2024', 2024, '23107.000001/2024-01',
 1, 'Edital', 6, 'Pregão - Eletrônico', 1, 'Aberto',
 1, 'Divulgada no PNCP', 'Aquisição de material de escritório para atendimento das necessidades administrativas',
 'Registro de preços por 12 meses', TRUE, NULL, NULL, NULL,
 50000.00, 45500.00, '2024-02-01 09:00:00', '2024-02-01 17:00:00', '2024-01-25',
 '2024-01-25', '2024-02-05', 1,
 '00000000000191', 'Ministério da Economia',
 'E', 'F', '160012', 'Secretaria de Gestão', 5300108,
 'Brasília', 'DF', 'Distrito Federal',
 'João Silva Santos', 'https://comprasnet.gov.br',
 current_timestamp, current_timestamp),

-- Dispensa para Serviços Emergenciais
('CNTP-2024-002', 'DL-002/2024', 2024, '23107.000002/2024-01',
 2, 'Aviso de Contratação Direta', 8, 'Dispensa de Licitação', 5, 'Não se Aplica',
 1, 'Divulgada no PNCP', 'Contratação emergencial de serviços de dedetização devido a infestação de pragas',
 'Contratação por emergência conforme Art. 75, IV', FALSE, 4, 'Lei 14.133/2021, Art. 75, IV',
 'Emergência ou calamidade pública', 15000.00, 14800.00,
 NULL, NULL, '2024-01-30',
 '2024-01-30', '2024-01-30', 1,
 '46522729000118', 'Prefeitura Municipal de São Paulo',
 'E', 'M', '010001', 'Secretaria de Administração', 3550308,
 'São Paulo', 'SP', 'São Paulo',
 'Maria Oliveira Costa', 'https://e-negociospublicos.com.br',
 current_timestamp, current_timestamp);

-- Insert sample contratação items
INSERT INTO item_contratacao (
    contratacao_id, ano_compra, numero_item, descricao_item,
    unidade_medida, quantidade, valor_unitario, valor_total,
    situacao_item_id, situacao_item_nome, tipo_beneficio_id,
    tipo_beneficio_nome, created_at, updated_at
) VALUES 
-- Items for first contratação
(1, 2024, 1, 'Papel sulfite A4 75g/m² branco, pacote com 500 folhas',
 'RESMA', 2000.00, 15.00, 30000.00,
 2, 'Homologado', 1, 'Participação Exclusiva ME/EPP',
 current_timestamp, current_timestamp),

(1, 2024, 2, 'Caneta esferográfica azul, corpo transparente',
 'UNIDADE', 1000.00, 1.50, 1500.00,
 2, 'Homologado', 1, 'Participação Exclusiva ME/EPP',
 current_timestamp, current_timestamp),

(1, 2024, 3, 'Grampeador de mesa para 25 folhas',
 'UNIDADE', 50.00, 25.00, 1250.00,
 2, 'Homologado', 1, 'Participação Exclusiva ME/EPP',
 current_timestamp, current_timestamp),

-- Items for second contratação
(2, 2024, 1, 'Serviços de dedetização e controle de pragas urbanas',
 'M²', 5000.00, 2.96, 14800.00,
 2, 'Homologado', 4, 'Sem Benefício',
 current_timestamp, current_timestamp);

-- ================================================
-- SAMPLE ATA DATA
-- ================================================

-- Insert sample atas
INSERT INTO ata_registro_preco (
    numero_controle_pncp_ata, numero_controle_pncp_compra,
    numero_ata_registro_preco, ano_ata, data_assinatura,
    vigencia_inicio, vigencia_fim, cancelado, data_publicacao_pncp,
    data_inclusao, data_atualizacao, objeto_contratacao,
    cnpj_orgao, nome_orgao, codigo_unidade_orgao, nome_unidade_orgao,
    usuario, created_at, updated_at
) VALUES 
('ATA-2024-001', 'CNTP-2024-001', 'ARP-001/2024', 2024, '2024-02-10',
 '2024-02-15', '2025-02-14', FALSE, '2024-02-12',
 '2024-02-12', '2024-02-12', 'Ata de Registro de Preços para aquisição de material de escritório',
 '00000000000191', 'Ministério da Economia', '160012', 'Secretaria de Gestão',
 'João Silva Santos', current_timestamp, current_timestamp);

-- ================================================
-- SAMPLE CONTRACT DATA
-- ================================================

-- Insert sample contracts
INSERT INTO contrato (
    numero_controle_pncp, numero_controle_pncp_compra,
    numero_contrato_empenho, ano_contrato, sequencial_contrato,
    processo, tipo_contrato_id, tipo_contrato_nome,
    categoria_processo_id, categoria_processo_nome, receita,
    objeto_contrato, informacao_complementar,
    orgao_entidade_cnpj, orgao_entidade_razao_social,
    orgao_entidade_poder_id, orgao_entidade_esfera_id,
    unidade_orgao_codigo, unidade_orgao_nome, unidade_orgao_codigo_ibge,
    unidade_orgao_municipio, unidade_orgao_uf_sigla, unidade_orgao_uf_nome,
    tipo_pessoa, ni_fornecedor, nome_razao_social_fornecedor,
    valor_inicial, numero_parcelas, valor_parcela, valor_global,
    data_assinatura, data_vigencia_inicio, data_vigencia_fim,
    data_publicacao_pncp, usuario_nome,
    created_at, updated_at
) VALUES 
-- Contract for emergency services
('CONT-2024-001', 'CNTP-2024-002', 'CT-001/2024', 2024, 1,
 '23107.000002/2024-01', 7, 'Empenho', 8, 'Serviços',
 FALSE, 'Contrato para prestação de serviços de dedetização e controle de pragas urbanas',
 'Execução imediata devido à emergência',
 '46522729000118', 'Prefeitura Municipal de São Paulo',
 'E', 'M', '010001', 'Secretaria de Administração', 3550308,
 'São Paulo', 'SP', 'São Paulo',
 'J', '12345678000195', 'Empresa de Dedetização Ltda',
 14800.00, 1, 14800.00, 14800.00,
 '2024-01-31', '2024-02-01', '2024-02-28',
 '2024-02-01 10:00:00', 'Maria Oliveira Costa',
 current_timestamp, current_timestamp);

-- ================================================
-- SAMPLE LOG DATA
-- ================================================

-- Insert sample logs
INSERT INTO log_sistema (
    nivel, modulo, mensagem, timestamp, user_id, request_id, detalhes,
    created_at, updated_at
) VALUES 
('INFO', 'authentication', 'User logged in successfully', '2024-01-25 08:30:00', 2, 'req-001', 
 '{"username": "gestor.compras", "ip": "192.168.1.100"}', current_timestamp, current_timestamp),

('INFO', 'pca_sync', 'PCA data synchronized from PNCP', '2024-01-25 09:00:00', NULL, 'sync-001',
 '{"records_processed": 150, "source": "PNCP_API"}', current_timestamp, current_timestamp),

('WARNING', 'contract_monitoring', 'Contract expiring soon', '2024-01-25 10:00:00', NULL, 'monitor-001',
 '{"contract_id": 1, "days_remaining": 30}', current_timestamp, current_timestamp),

('ERROR', 'pncp_integration', 'Failed to connect to PNCP API', '2024-01-25 11:30:00', NULL, 'api-001',
 '{"error": "Connection timeout", "url": "https://pncp.gov.br/api/consulta"}', current_timestamp, current_timestamp),

('INFO', 'system', 'Database maintenance completed', '2024-01-25 02:00:00', NULL, 'maint-001',
 '{"operation": "vacuum_analyze", "duration": "45 minutes"}', current_timestamp, current_timestamp);

-- ================================================
-- SAMPLE MONITORING DATA
-- ================================================

-- Insert sample monitoring data
INSERT INTO monitoring.database_stats (
    table_name, total_rows, total_size_bytes, index_size_bytes,
    last_vacuum, last_analyze, collected_at
) VALUES 
('usuario', 4, 32768, 16384, '2024-01-25 02:00:00', '2024-01-25 02:00:00', current_timestamp),
('contratacao', 2, 65536, 32768, '2024-01-25 02:00:00', '2024-01-25 02:00:00', current_timestamp),
('pca', 2, 49152, 24576, '2024-01-25 02:00:00', '2024-01-25 02:00:00', current_timestamp),
('log_sistema', 5, 81920, 40960, '2024-01-25 02:00:00', '2024-01-25 02:00:00', current_timestamp);

INSERT INTO monitoring.query_performance (
    query_hash, query_text, total_calls, total_time_ms, mean_time_ms,
    min_time_ms, max_time_ms, collected_at
) VALUES 
('abc123def456', 'SELECT * FROM contratacao WHERE modalidade_id = $1', 150, 1250.5, 8.3, 2.1, 45.7, current_timestamp),
('def456ghi789', 'SELECT * FROM pca WHERE ano_pca = $1', 75, 625.2, 8.3, 1.8, 32.4, current_timestamp),
('ghi789jkl012', 'SELECT * FROM usuario WHERE username = $1', 300, 450.8, 1.5, 0.8, 12.3, current_timestamp);

-- ================================================
-- REFRESH MATERIALIZED VIEWS AND STATISTICS
-- ================================================

-- Update table statistics
ANALYZE usuario;
ANALYZE configuracao_sistema;
ANALYZE modalidade_contratacao;
ANALYZE situacao_contratacao;
ANALYZE modo_disputa;
ANALYZE amparo_legal;
ANALYZE pca;
ANALYZE item_pca;
ANALYZE contratacao;
ANALYZE item_contratacao;
ANALYZE ata_registro_preco;
ANALYZE contrato;
ANALYZE log_sistema;

-- Log completion of sample data insertion
INSERT INTO log_sistema (nivel, modulo, mensagem, timestamp, detalhes, created_at, updated_at)
VALUES (
    'INFO',
    'database_setup',
    'Sample data insertion completed',
    current_timestamp,
    jsonb_build_object(
        'users_created', 4,
        'configurations_created', 10,
        'pca_records', 2,
        'contratacao_records', 2,
        'contracts_created', 1,
        'atas_created', 1
    ),
    current_timestamp,
    current_timestamp
);

COMMIT;
