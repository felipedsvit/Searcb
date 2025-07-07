#!/usr/bin/env python3
"""
Script para criar as tabelas do banco de dados
"""
import os
import sys
sys.path.append('/app')

from app.core.database import engine
from app.models import Base
from app.models.usuario import LogSistema, ConfiguracaoSistema
from sqlalchemy import text
from datetime import datetime

def create_tables():
    """Criar todas as tabelas"""
    print("Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

def insert_default_configs():
    """Inserir configurações padrão"""
    with engine.connect() as conn:
        # Verificar se já existem configurações
        result = conn.execute(text('SELECT COUNT(*) FROM configuracao_sistema'))
        count = result.fetchone()[0]
        
        if count == 0:
            # Inserir configurações padrão
            configs = [
                ('pncp_sync_interval', '3600', 'Intervalo de sincronização com PNCP (segundos)', 'integracao', 'INTEGER'),
                ('max_page_size', '500', 'Tamanho máximo de página para consultas', 'api', 'INTEGER'),
                ('cache_ttl', '3600', 'Tempo de vida do cache (segundos)', 'cache', 'INTEGER'),
                ('rate_limit_requests', '100', 'Limite de requisições por minuto', 'seguranca', 'INTEGER'),
                ('email_notifications', 'true', 'Habilitar notificações por email', 'notificacoes', 'BOOLEAN')
            ]
            
            for chave, valor, descricao, categoria, tipo in configs:
                conn.execute(text('''
                    INSERT INTO configuracao_sistema 
                    (chave, valor, descricao, categoria, tipo, ativo, somente_leitura, valor_padrao, created_at, updated_at)
                    VALUES (:chave, :valor, :descricao, :categoria, :tipo, true, false, :valor_padrao, NOW(), NOW())
                '''), {
                    'chave': chave,
                    'valor': valor,
                    'descricao': descricao,
                    'categoria': categoria,
                    'tipo': tipo,
                    'valor_padrao': valor
                })
            
            conn.commit()
            print(f'Configurações padrão inseridas com sucesso!')
        else:
            print(f'Já existem {count} configurações no banco')

if __name__ == '__main__':
    create_tables()
    insert_default_configs()
