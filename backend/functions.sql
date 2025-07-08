-- ================================================
-- SEARCB Database Functions
-- PL/pgSQL functions for complex operations
-- ================================================

SET search_path TO searcb, public;

-- ================================================
-- HEALTH CHECK FUNCTIONS
-- ================================================

CREATE OR REPLACE FUNCTION health_check()
RETURNS TABLE(
    component TEXT,
    status TEXT,
    details JSONB,
    checked_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    -- Database connectivity
    RETURN QUERY SELECT 
        'database'::TEXT,
        'healthy'::TEXT,
        jsonb_build_object(
            'version', version(),
            'uptime', current_timestamp - pg_postmaster_start_time(),
            'connections', (SELECT count(*) FROM pg_stat_activity)
        ),
        current_timestamp;
    
    -- Table status
    RETURN QUERY SELECT 
        'tables'::TEXT,
        CASE 
            WHEN count(*) > 0 THEN 'healthy'::TEXT
            ELSE 'warning'::TEXT
        END,
        jsonb_build_object(
            'total_tables', count(*),
            'schema', 'searcb'
        ),
        current_timestamp
    FROM information_schema.tables 
    WHERE table_schema = 'searcb';
    
    -- Recent activity check
    RETURN QUERY SELECT 
        'activity'::TEXT,
        CASE 
            WHEN EXISTS (SELECT 1 FROM log_sistema WHERE timestamp > current_timestamp - INTERVAL '1 hour')
            THEN 'active'::TEXT
            ELSE 'idle'::TEXT
        END,
        jsonb_build_object(
            'recent_logs', (SELECT count(*) FROM log_sistema WHERE timestamp > current_timestamp - INTERVAL '1 hour'),
            'total_logs', (SELECT count(*) FROM log_sistema)
        ),
        current_timestamp;
        
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- USER MANAGEMENT FUNCTIONS
-- ================================================

CREATE OR REPLACE FUNCTION create_user_with_profile(
    p_username VARCHAR(50),
    p_email VARCHAR(255),
    p_senha_hash VARCHAR(255),
    p_nome_completo VARCHAR(255),
    p_telefone VARCHAR(20) DEFAULT NULL,
    p_cargo VARCHAR(100) DEFAULT NULL,
    p_orgao_cnpj VARCHAR(14) DEFAULT NULL,
    p_orgao_nome VARCHAR(255) DEFAULT NULL,
    p_is_admin BOOLEAN DEFAULT FALSE,
    p_is_gestor BOOLEAN DEFAULT FALSE,
    p_is_operador BOOLEAN DEFAULT TRUE
)
RETURNS INTEGER AS $$
DECLARE
    user_id INTEGER;
BEGIN
    -- Validate email format
    IF p_email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        RAISE EXCEPTION 'Invalid email format: %', p_email;
    END IF;
    
    -- Validate CNPJ format if provided
    IF p_orgao_cnpj IS NOT NULL AND p_orgao_cnpj !~ '^[0-9]{14}$' THEN
        RAISE EXCEPTION 'Invalid CNPJ format: %', p_orgao_cnpj;
    END IF;
    
    -- Insert user
    INSERT INTO usuario (
        username, email, senha_hash, nome_completo, telefone, cargo,
        orgao_cnpj, orgao_nome, is_admin, is_gestor, is_operador,
        created_at, updated_at
    ) VALUES (
        p_username, p_email, p_senha_hash, p_nome_completo, p_telefone, p_cargo,
        p_orgao_cnpj, p_orgao_nome, p_is_admin, p_is_gestor, p_is_operador,
        current_timestamp, current_timestamp
    ) RETURNING id INTO user_id;
    
    -- Log user creation
    INSERT INTO log_sistema (nivel, modulo, mensagem, user_id, detalhes)
    VALUES (
        'INFO', 
        'user_management', 
        'User created successfully',
        user_id,
        jsonb_build_object(
            'username', p_username,
            'email', p_email,
            'roles', jsonb_build_object(
                'admin', p_is_admin,
                'gestor', p_is_gestor,
                'operador', p_is_operador
            )
        )
    );
    
    RETURN user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- PCA MANAGEMENT FUNCTIONS
-- ================================================

CREATE OR REPLACE FUNCTION sync_pca_from_pncp(
    p_ano_pca INTEGER,
    p_pca_data JSONB
)
RETURNS INTEGER AS $$
DECLARE
    pca_id INTEGER;
    item_data JSONB;
    items_inserted INTEGER := 0;
BEGIN
    -- Validate year
    IF p_ano_pca < 2000 OR p_ano_pca > 2050 THEN
        RAISE EXCEPTION 'Invalid PCA year: %', p_ano_pca;
    END IF;
    
    -- Insert or update PCA
    INSERT INTO pca (
        id_pca_pncp, ano_pca, data_publicacao_pncp,
        orgao_entidade_cnpj, orgao_entidade_razao_social,
        codigo_unidade, nome_unidade,
        created_at, updated_at
    ) VALUES (
        p_pca_data->>'idPcaPncp',
        p_ano_pca,
        (p_pca_data->>'dataPublicacaoPncp')::DATE,
        p_pca_data->>'orgaoEntidadeCnpj',
        p_pca_data->>'orgaoEntidadeRazaoSocial',
        p_pca_data->>'codigoUnidade',
        p_pca_data->>'nomeUnidade',
        current_timestamp,
        current_timestamp
    )
    ON CONFLICT (id_pca_pncp) 
    DO UPDATE SET
        data_publicacao_pncp = EXCLUDED.data_publicacao_pncp,
        orgao_entidade_razao_social = EXCLUDED.orgao_entidade_razao_social,
        nome_unidade = EXCLUDED.nome_unidade,
        updated_at = current_timestamp
    RETURNING id INTO pca_id;
    
    -- Process PCA items if provided
    IF p_pca_data ? 'itens' THEN
        FOR item_data IN SELECT jsonb_array_elements(p_pca_data->'itens')
        LOOP
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
            ) VALUES (
                pca_id,
                (item_data->>'numeroItem')::INTEGER,
                item_data->>'categoriaItemPcaNome',
                item_data->>'classificacaoCatalogoId',
                item_data->>'nomeClassificacaoCatalogo',
                item_data->>'classificacaoSuperiorCodigo',
                item_data->>'classificacaoSuperiorNome',
                item_data->>'pdmCodigo',
                item_data->>'pdmDescricao',
                item_data->>'codigoItem',
                item_data->>'descricaoItem',
                item_data->>'unidadeFornecimento',
                (item_data->>'quantidadeEstimada')::DECIMAL,
                (item_data->>'valorUnitario')::DECIMAL,
                (item_data->>'valorTotal')::DECIMAL,
                (item_data->>'valorOrcamentoExercicio')::DECIMAL,
                (item_data->>'dataDesejada')::DATE,
                item_data->>'unidadeRequisitante',
                item_data->>'grupoContratacaoCodigo',
                item_data->>'grupoContratacaoNome',
                (item_data->>'dataInclusao')::DATE,
                (item_data->>'dataAtualizacao')::DATE,
                current_timestamp,
                current_timestamp
            )
            ON CONFLICT (pca_id, numero_item)
            DO UPDATE SET
                descricao_item = EXCLUDED.descricao_item,
                quantidade_estimada = EXCLUDED.quantidade_estimada,
                valor_unitario = EXCLUDED.valor_unitario,
                valor_total = EXCLUDED.valor_total,
                data_atualizacao = EXCLUDED.data_atualizacao,
                updated_at = current_timestamp;
            
            items_inserted := items_inserted + 1;
        END LOOP;
    END IF;
    
    -- Log synchronization
    INSERT INTO log_sistema (nivel, modulo, mensagem, detalhes)
    VALUES (
        'INFO',
        'pca_sync',
        'PCA synchronized from PNCP',
        jsonb_build_object(
            'pca_id', pca_id,
            'ano_pca', p_ano_pca,
            'items_processed', items_inserted
        )
    );
    
    RETURN pca_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- SEARCH FUNCTIONS
-- ================================================

CREATE OR REPLACE FUNCTION search_contratacoes(
    p_termo_busca TEXT DEFAULT NULL,
    p_modalidade_id INTEGER DEFAULT NULL,
    p_situacao_compra_id INTEGER DEFAULT NULL,
    p_uf VARCHAR(2) DEFAULT NULL,
    p_cnpj VARCHAR(14) DEFAULT NULL,
    p_data_inicial DATE DEFAULT NULL,
    p_data_final DATE DEFAULT NULL,
    p_valor_minimo DECIMAL DEFAULT NULL,
    p_valor_maximo DECIMAL DEFAULT NULL,
    p_limit INTEGER DEFAULT 50,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE(
    id INTEGER,
    numero_controle_pncp VARCHAR(50),
    numero_compra VARCHAR(50),
    modalidade_nome VARCHAR(100),
    situacao_compra_nome VARCHAR(100),
    objeto_compra TEXT,
    valor_total_estimado DECIMAL,
    data_publicacao_pncp DATE,
    orgao_entidade_razao_social VARCHAR(255),
    unidade_orgao_uf_sigla VARCHAR(2),
    relevancia REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.numero_controle_pncp,
        c.numero_compra,
        c.modalidade_nome,
        c.situacao_compra_nome,
        c.objeto_compra,
        c.valor_total_estimado,
        c.data_publicacao_pncp,
        c.orgao_entidade_razao_social,
        c.unidade_orgao_uf_sigla,
        CASE 
            WHEN p_termo_busca IS NOT NULL THEN
                ts_rank(to_tsvector('portuguese', c.objeto_compra), 
                       plainto_tsquery('portuguese', p_termo_busca))
            ELSE 1.0
        END::REAL AS relevancia
    FROM contratacao c
    WHERE (p_termo_busca IS NULL OR 
           to_tsvector('portuguese', c.objeto_compra) @@ plainto_tsquery('portuguese', p_termo_busca))
    AND (p_modalidade_id IS NULL OR c.modalidade_id = p_modalidade_id)
    AND (p_situacao_compra_id IS NULL OR c.situacao_compra_id = p_situacao_compra_id)
    AND (p_uf IS NULL OR c.unidade_orgao_uf_sigla = p_uf)
    AND (p_cnpj IS NULL OR c.orgao_entidade_cnpj = p_cnpj)
    AND (p_data_inicial IS NULL OR c.data_publicacao_pncp >= p_data_inicial)
    AND (p_data_final IS NULL OR c.data_publicacao_pncp <= p_data_final)
    AND (p_valor_minimo IS NULL OR c.valor_total_estimado >= p_valor_minimo)
    AND (p_valor_maximo IS NULL OR c.valor_total_estimado <= p_valor_maximo)
    ORDER BY 
        CASE WHEN p_termo_busca IS NOT NULL 
             THEN ts_rank(to_tsvector('portuguese', c.objeto_compra), 
                         plainto_tsquery('portuguese', p_termo_busca))
             ELSE 0 
        END DESC,
        c.data_publicacao_pncp DESC
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- STATISTICS AND REPORTING FUNCTIONS
-- ================================================

CREATE OR REPLACE FUNCTION get_contratacao_statistics(
    p_data_inicial DATE DEFAULT NULL,
    p_data_final DATE DEFAULT NULL,
    p_uf VARCHAR(2) DEFAULT NULL
)
RETURNS TABLE(
    total_contratacoes BIGINT,
    valor_total DECIMAL,
    modalidade_mais_comum VARCHAR(100),
    orgao_mais_ativo VARCHAR(255),
    media_valor_estimado DECIMAL,
    periodo_analise JSONB
) AS $$
DECLARE
    v_data_inicial DATE;
    v_data_final DATE;
BEGIN
    -- Set default dates if not provided
    v_data_inicial := COALESCE(p_data_inicial, CURRENT_DATE - INTERVAL '30 days');
    v_data_final := COALESCE(p_data_final, CURRENT_DATE);
    
    RETURN QUERY
    WITH stats AS (
        SELECT 
            count(*) as total_count,
            sum(c.valor_total_estimado) as total_value,
            avg(c.valor_total_estimado) as avg_value
        FROM contratacao c
        WHERE c.data_publicacao_pncp BETWEEN v_data_inicial AND v_data_final
        AND (p_uf IS NULL OR c.unidade_orgao_uf_sigla = p_uf)
    ),
    top_modalidade AS (
        SELECT c.modalidade_nome
        FROM contratacao c
        WHERE c.data_publicacao_pncp BETWEEN v_data_inicial AND v_data_final
        AND (p_uf IS NULL OR c.unidade_orgao_uf_sigla = p_uf)
        GROUP BY c.modalidade_nome
        ORDER BY count(*) DESC
        LIMIT 1
    ),
    top_orgao AS (
        SELECT c.orgao_entidade_razao_social
        FROM contratacao c
        WHERE c.data_publicacao_pncp BETWEEN v_data_inicial AND v_data_final
        AND (p_uf IS NULL OR c.unidade_orgao_uf_sigla = p_uf)
        GROUP BY c.orgao_entidade_razao_social
        ORDER BY count(*) DESC
        LIMIT 1
    )
    SELECT 
        s.total_count,
        s.total_value,
        tm.modalidade_nome,
        to.orgao_entidade_razao_social,
        s.avg_value,
        jsonb_build_object(
            'data_inicial', v_data_inicial,
            'data_final', v_data_final,
            'uf', p_uf,
            'dias_periodo', v_data_final - v_data_inicial
        )
    FROM stats s, top_modalidade tm, top_orgao to;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- CLEANUP AND MAINTENANCE FUNCTIONS
-- ================================================

CREATE OR REPLACE FUNCTION cleanup_old_logs(
    p_retention_days INTEGER DEFAULT 90
)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
    cutoff_date TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Calculate cutoff date
    cutoff_date := current_timestamp - (p_retention_days || ' days')::INTERVAL;
    
    -- Delete old logs
    DELETE FROM log_sistema 
    WHERE timestamp < cutoff_date
    AND nivel NOT IN ('ERROR', 'CRITICAL'); -- Keep error logs longer
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log cleanup operation
    INSERT INTO log_sistema (nivel, modulo, mensagem, detalhes)
    VALUES (
        'INFO',
        'maintenance',
        'Log cleanup completed',
        jsonb_build_object(
            'deleted_count', deleted_count,
            'retention_days', p_retention_days,
            'cutoff_date', cutoff_date
        )
    );
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION update_table_statistics()
RETURNS VOID AS $$
DECLARE
    table_record RECORD;
BEGIN
    -- Update statistics for all main tables
    FOR table_record IN 
        SELECT schemaname, tablename 
        FROM pg_tables 
        WHERE schemaname = 'searcb'
        AND tablename NOT LIKE '%_prt_%'  -- Skip partition tables
    LOOP
        EXECUTE format('ANALYZE %I.%I', table_record.schemaname, table_record.tablename);
    END LOOP;
    
    -- Insert statistics into monitoring table
    INSERT INTO monitoring.database_stats (
        table_name, total_rows, total_size_bytes, index_size_bytes,
        last_vacuum, last_analyze, collected_at
    )
    SELECT 
        schemaname || '.' || tablename as table_name,
        n_tup_ins + n_tup_upd + n_tup_del as total_rows,
        pg_total_relation_size(schemaname||'.'||tablename) as total_size_bytes,
        pg_indexes_size(schemaname||'.'||tablename) as index_size_bytes,
        last_vacuum,
        last_analyze,
        current_timestamp
    FROM pg_stat_user_tables
    WHERE schemaname = 'searcb'
    ON CONFLICT (table_name, collected_at) DO NOTHING;
    
    -- Log statistics update
    INSERT INTO log_sistema (nivel, modulo, mensagem)
    VALUES (
        'INFO',
        'maintenance', 
        'Database statistics updated'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- VALIDATION FUNCTIONS
-- ================================================

CREATE OR REPLACE FUNCTION validate_cnpj(cnpj_input TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    cnpj_clean TEXT;
    dig1 INTEGER;
    dig2 INTEGER;
    calc INTEGER;
    i INTEGER;
BEGIN
    -- Remove non-numeric characters
    cnpj_clean := regexp_replace(cnpj_input, '[^0-9]', '', 'g');
    
    -- Check length
    IF length(cnpj_clean) != 14 THEN
        RETURN FALSE;
    END IF;
    
    -- Check for invalid patterns
    IF cnpj_clean IN ('00000000000000', '11111111111111', '22222222222222', 
                      '33333333333333', '44444444444444', '55555555555555',
                      '66666666666666', '77777777777777', '88888888888888', 
                      '99999999999999') THEN
        RETURN FALSE;
    END IF;
    
    -- Calculate first check digit
    calc := 0;
    FOR i IN 1..12 LOOP
        calc := calc + substring(cnpj_clean, i, 1)::INTEGER * 
                CASE WHEN i <= 4 THEN (6 - i) ELSE (14 - i) END;
    END LOOP;
    
    dig1 := CASE WHEN (calc % 11) < 2 THEN 0 ELSE (11 - (calc % 11)) END;
    
    -- Calculate second check digit
    calc := 0;
    FOR i IN 1..13 LOOP
        calc := calc + substring(cnpj_clean, i, 1)::INTEGER * 
                CASE WHEN i <= 5 THEN (7 - i) ELSE (15 - i) END;
    END LOOP;
    
    dig2 := CASE WHEN (calc % 11) < 2 THEN 0 ELSE (11 - (calc % 11)) END;
    
    -- Validate check digits
    RETURN (substring(cnpj_clean, 13, 1)::INTEGER = dig1 AND 
            substring(cnpj_clean, 14, 1)::INTEGER = dig2);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ================================================
-- NOTIFICATION FUNCTIONS
-- ================================================

CREATE OR REPLACE FUNCTION notify_contract_expiring()
RETURNS INTEGER AS $$
DECLARE
    contract_record RECORD;
    notification_count INTEGER := 0;
BEGIN
    -- Find contracts expiring in the next 30 days
    FOR contract_record IN 
        SELECT id, numero_controle_pncp, data_vigencia_fim, 
               orgao_entidade_razao_social, valor_global
        FROM contrato
        WHERE data_vigencia_fim BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
        AND data_vigencia_fim IS NOT NULL
    LOOP
        -- Log notification
        INSERT INTO log_sistema (nivel, modulo, mensagem, detalhes)
        VALUES (
            'WARNING',
            'contract_monitoring',
            'Contract expiring soon',
            jsonb_build_object(
                'contract_id', contract_record.id,
                'numero_controle_pncp', contract_record.numero_controle_pncp,
                'data_vigencia_fim', contract_record.data_vigencia_fim,
                'dias_restantes', contract_record.data_vigencia_fim - CURRENT_DATE,
                'orgao', contract_record.orgao_entidade_razao_social,
                'valor_global', contract_record.valor_global
            )
        );
        
        notification_count := notification_count + 1;
    END LOOP;
    
    RETURN notification_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- CREATE VIEWS
-- ================================================

CREATE OR REPLACE VIEW vw_contratacoes_resumo AS
SELECT 
    c.id,
    c.numero_controle_pncp,
    c.numero_compra,
    c.ano_compra,
    c.modalidade_nome,
    c.situacao_compra_nome,
    c.objeto_compra,
    c.valor_total_estimado,
    c.valor_total_homologado,
    c.data_publicacao_pncp,
    c.orgao_entidade_cnpj,
    c.orgao_entidade_razao_social,
    c.unidade_orgao_uf_sigla,
    c.unidade_orgao_municipio,
    count(ic.id) as total_itens,
    sum(ic.valor_total) as valor_total_itens
FROM contratacao c
LEFT JOIN item_contratacao ic ON c.id = ic.contratacao_id AND c.ano_compra = ic.ano_compra
GROUP BY c.id, c.numero_controle_pncp, c.numero_compra, c.ano_compra, 
         c.modalidade_nome, c.situacao_compra_nome, c.objeto_compra,
         c.valor_total_estimado, c.valor_total_homologado, c.data_publicacao_pncp,
         c.orgao_entidade_cnpj, c.orgao_entidade_razao_social, 
         c.unidade_orgao_uf_sigla, c.unidade_orgao_municipio;

-- ================================================
-- CREATE SCHEDULED JOBS (if pg_cron is available)
-- ================================================

-- Note: These would require pg_cron extension
-- SELECT cron.schedule('cleanup-old-logs', '0 2 * * *', 'SELECT searcb.cleanup_old_logs(90);');
-- SELECT cron.schedule('update-statistics', '0 3 * * *', 'SELECT searcb.update_table_statistics();');
-- SELECT cron.schedule('contract-notifications', '0 9 * * *', 'SELECT searcb.notify_contract_expiring();');

COMMIT;
