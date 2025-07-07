"""Initial migration with logs and configs

Revision ID: 0001
Revises: 
Create Date: 2025-07-07 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create tables that don't exist yet
    
    # Create log_sistema table if it doesn't exist
    op.create_table(
        'log_sistema',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nivel', sa.String(20), nullable=False),
        sa.Column('categoria', sa.String(50), nullable=False),
        sa.Column('modulo', sa.String(100), nullable=True),
        sa.Column('mensagem', sa.Text(), nullable=False),
        sa.Column('detalhes', sa.Text(), nullable=True),
        sa.Column('ip_origem', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('endpoint', sa.String(200), nullable=True),
        sa.Column('metodo_http', sa.String(10), nullable=True),
        sa.Column('tempo_processamento', sa.Integer(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('contexto_adicional', sa.Text(), nullable=True),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'])
    )
    
    # Create indices for log_sistema
    op.create_index('ix_log_sistema_nivel', 'log_sistema', ['nivel'])
    op.create_index('ix_log_sistema_categoria', 'log_sistema', ['categoria'])
    op.create_index('ix_log_sistema_created_at', 'log_sistema', ['created_at'])
    op.create_index('ix_log_sistema_usuario_id', 'log_sistema', ['usuario_id'])
    
    # Create configuracao_sistema table if it doesn't exist
    op.create_table(
        'configuracao_sistema',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chave', sa.String(100), nullable=False, unique=True),
        sa.Column('valor', sa.Text(), nullable=True),
        sa.Column('tipo', sa.String(20), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('categoria', sa.String(50), nullable=True),
        sa.Column('ativo', sa.Boolean(), default=True),
        sa.Column('somente_leitura', sa.Boolean(), default=False),
        sa.Column('valor_padrao', sa.Text(), nullable=True),
        sa.Column('valor_minimo', sa.Text(), nullable=True),
        sa.Column('valor_maximo', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Create indices for configuracao_sistema
    op.create_index('ix_configuracao_sistema_chave', 'configuracao_sistema', ['chave'])
    op.create_index('ix_configuracao_sistema_categoria', 'configuracao_sistema', ['categoria'])
    op.create_index('ix_configuracao_sistema_ativo', 'configuracao_sistema', ['ativo'])
    
    # Insert default configurations
    op.execute("""
        INSERT INTO configuracao_sistema (chave, valor, descricao, categoria, tipo, ativo, somente_leitura, valor_padrao, created_at, updated_at)
        VALUES 
        ('pncp_sync_interval', '3600', 'Intervalo de sincronização com PNCP (segundos)', 'integracao', 'INTEGER', true, false, '3600', NOW(), NOW()),
        ('max_page_size', '500', 'Tamanho máximo de página para consultas', 'api', 'INTEGER', true, false, '500', NOW(), NOW()),
        ('cache_ttl', '3600', 'Tempo de vida do cache (segundos)', 'cache', 'INTEGER', true, false, '3600', NOW(), NOW()),
        ('rate_limit_requests', '100', 'Limite de requisições por minuto', 'seguranca', 'INTEGER', true, false, '100', NOW(), NOW()),
        ('email_notifications', 'true', 'Habilitar notificações por email', 'notificacoes', 'BOOLEAN', true, false, 'true', NOW(), NOW())
    """)


def downgrade():
    # Drop tables
    op.drop_table('configuracao_sistema')
    op.drop_table('log_sistema')
