"""
Tasks Celery para processamento em background
"""

from .sync_tasks import celery_app
from .background_tasks import (
    processo_sincronizacao_completa,
    processo_limpeza_cache,
    processo_backup_dados,
    processo_relatorio_diario,
    processo_monitoramento_sistema,
    processo_notificacao_usuario,
    processo_validacao_dados
)

__all__ = [
    "celery_app",
    "processo_sincronizacao_completa",
    "processo_limpeza_cache",
    "processo_backup_dados",
    "processo_relatorio_diario",
    "processo_monitoramento_sistema",
    "processo_notificacao_usuario",
    "processo_validacao_dados"
]