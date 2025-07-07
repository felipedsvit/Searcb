"""
Tasks Celery para processamento em background
"""
import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import logging

from celery import Celery
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.pncp_service import pncp_service
from app.models.pca import PCA
from app.models.contratacao import Contratacao
from app.models.ata import AtaRegistroPreco
from app.models.contrato import Contrato
from app.core.cache import clear_cache_pattern

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instância do Celery
celery_app = Celery(
    "searcb_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.sync_tasks"]
)

# Configuração do Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configuração de schedule
celery_app.conf.beat_schedule = {
    "sync-pncp-daily": {
        "task": "app.tasks.sync_tasks.sync_pncp_data",
        "schedule": 24 * 60 * 60,  # Diário
        "args": (),
    },
    "sync-domain-tables": {
        "task": "app.tasks.sync_tasks.sync_domain_tables",
        "schedule": 7 * 24 * 60 * 60,  # Semanal
        "args": (),
    },
    "cleanup-expired-cache": {
        "task": "app.tasks.sync_tasks.cleanup_expired_cache",
        "schedule": 60 * 60,  # A cada hora
        "args": (),
    },
    "check-contract-expiry": {
        "task": "app.tasks.sync_tasks.check_contract_expiry",
        "schedule": 24 * 60 * 60,  # Diário
        "args": (),
    },
    "generate-daily-reports": {
        "task": "app.tasks.sync_tasks.generate_daily_reports",
        "schedule": 24 * 60 * 60,  # Diário
        "args": (),
    },
}


def get_db() -> Session:
    """
    Obtém sessão do banco de dados
    """
    db = SessionLocal()
    try:
        return db
    finally:
        pass


async def run_async_task(coro):
    """
    Executa tarefa assíncrona
    """
    return await coro


@celery_app.task(bind=True, max_retries=3)
def sync_pncp_data(self, data_inicio: Optional[str] = None, data_fim: Optional[str] = None):
    """
    Sincroniza dados do PNCP
    """
    try:
        logger.info("Iniciando sincronização com PNCP")
        
        # Converter datas se fornecidas
        if data_inicio:
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        else:
            data_inicio = date.today() - timedelta(days=1)  # Ontem
        
        if data_fim:
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
        else:
            data_fim = date.today()
        
        # Executar sincronização
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            pncp_service.sincronizar_dados(data_inicio, data_fim)
        )
        
        loop.close()
        
        # Limpar cache relacionado
        asyncio.run(clear_cache_pattern("pncp_*"))
        asyncio.run(clear_cache_pattern("*_stats_*"))
        
        logger.info(f"Sincronização concluída: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Erro na sincronização PNCP: {e}")
        # Retry com backoff exponencial
        retry_delay = 2 ** self.request.retries
        raise self.retry(exc=e, countdown=retry_delay)


@celery_app.task(bind=True, max_retries=2)
def sync_domain_tables(self):
    """
    Sincroniza tabelas de domínio (modalidades, situações, etc.)
    """
    try:
        logger.info("Sincronizando tabelas de domínio")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Sincronizar modalidades
        modalidades = loop.run_until_complete(pncp_service.obter_modalidades())
        
        # Sincronizar situações
        situacoes = loop.run_until_complete(pncp_service.obter_situacoes())
        
        # Sincronizar órgãos (amostra)
        orgaos = loop.run_until_complete(pncp_service.obter_orgaos(tamanho=100))
        
        loop.close()
        
        result = {
            "modalidades": len(modalidades),
            "situacoes": len(situacoes),
            "orgaos": len(orgaos.get("data", []))
        }
        
        logger.info(f"Tabelas de domínio sincronizadas: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao sincronizar tabelas de domínio: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task
def cleanup_expired_cache():
    """
    Limpa cache expirado
    """
    try:
        logger.info("Limpando cache expirado")
        
        # Esta função seria implementada no serviço de cache
        # Por enquanto, apenas log
        
        logger.info("Cache limpo")
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise


@celery_app.task
def check_contract_expiry():
    """
    Verifica contratos próximos do vencimento
    """
    try:
        logger.info("Verificando contratos próximos do vencimento")
        
        db = get_db()
        
        # Contratos vencendo em 30 dias
        data_limite = date.today() + timedelta(days=30)
        
        contratos_vencendo = db.query(Contrato).filter(
            Contrato.data_vigencia_fim <= data_limite
        ).all()
        
        # Contratos vencendo em 7 dias (alerta crítico)
        data_limite_critica = date.today() + timedelta(days=7)
        
        contratos_criticos = db.query(Contrato).filter(
            Contrato.data_vigencia_fim <= data_limite_critica
        ).all()
        
        # Aqui você poderia enviar notificações, emails, etc.
        
        result = {
            "contratos_vencendo_30_dias": len(contratos_vencendo),
            "contratos_vencendo_7_dias": len(contratos_criticos),
            "contratos_criticos": [
                {
                    "id": c.id,
                    "numero": c.numero_contrato_empenho,
                    "orgao": c.orgao_entidade_razao_social,
                    "data_fim": c.data_vigencia_fim.isoformat() if c.data_vigencia_fim else None
                }
                for c in contratos_criticos
            ]
        }
        
        logger.info(f"Verificação de vencimento concluída: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao verificar vencimento de contratos: {e}")
        raise
    finally:
        db.close()


@celery_app.task
def generate_daily_reports():
    """
    Gera relatórios diários
    """
    try:
        logger.info("Gerando relatórios diários")
        
        db = get_db()
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        
        # Estatísticas do dia anterior
        pcas_criados = db.query(PCA).filter(
            PCA.created_at >= ontem,
            PCA.created_at < hoje
        ).count()
        
        contratacoes_criadas = db.query(Contratacao).filter(
            Contratacao.created_at >= ontem,
            Contratacao.created_at < hoje
        ).count()
        
        atas_criadas = db.query(AtaRegistroPreco).filter(
            AtaRegistroPreco.created_at >= ontem,
            AtaRegistroPreco.created_at < hoje
        ).count()
        
        contratos_criados = db.query(Contrato).filter(
            Contrato.created_at >= ontem,
            Contrato.created_at < hoje
        ).count()
        
        # Valor total dos contratos criados
        from sqlalchemy import func
        valor_contratos = db.query(
            func.sum(Contrato.valor_inicial)
        ).filter(
            Contrato.created_at >= ontem,
            Contrato.created_at < hoje
        ).scalar() or 0
        
        report = {
            "data": ontem.isoformat(),
            "pcas_criados": pcas_criados,
            "contratacoes_criadas": contratacoes_criadas,
            "atas_criadas": atas_criadas,
            "contratos_criados": contratos_criados,
            "valor_total_contratos": float(valor_contratos)
        }
        
        logger.info(f"Relatório diário gerado: {report}")
        return report
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório diário: {e}")
        raise
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def sync_specific_entity(self, entity_type: str, entity_id: str):
    """
    Sincroniza entidade específica do PNCP
    """
    try:
        logger.info(f"Sincronizando {entity_type} ID: {entity_id}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = None
        
        if entity_type == "pca":
            result = loop.run_until_complete(pncp_service.obter_pca_por_id(entity_id))
        elif entity_type == "contratacao":
            result = loop.run_until_complete(pncp_service.obter_contratacao_por_id(entity_id))
        elif entity_type == "ata":
            result = loop.run_until_complete(pncp_service.obter_ata_por_id(entity_id))
        elif entity_type == "contrato":
            result = loop.run_until_complete(pncp_service.obter_contrato_por_id(entity_id))
        else:
            raise ValueError(f"Tipo de entidade inválido: {entity_type}")
        
        loop.close()
        
        logger.info(f"Sincronização de {entity_type} {entity_id} concluída")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao sincronizar {entity_type} {entity_id}: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task
def update_cache_stats():
    """
    Atualiza estatísticas em cache
    """
    try:
        logger.info("Atualizando estatísticas em cache")
        
        db = get_db()
        
        # Estatísticas gerais
        total_pcas = db.query(PCA).count()
        total_contratacoes = db.query(Contratacao).count()
        total_atas = db.query(AtaRegistroPreco).count()
        total_contratos = db.query(Contrato).count()
        
        # Valor total dos contratos
        from sqlalchemy import func
        valor_total = db.query(
            func.sum(Contrato.valor_inicial)
        ).scalar() or 0
        
        stats = {
            "total_pcas": total_pcas,
            "total_contratacoes": total_contratacoes,
            "total_atas": total_atas,
            "total_contratos": total_contratos,
            "valor_total_contratos": float(valor_total),
            "ultima_atualizacao": datetime.now().isoformat()
        }
        
        # Salvar no cache
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from app.core.cache import set_cache
        loop.run_until_complete(set_cache("stats_gerais", stats, expire=3600))
        
        loop.close()
        
        logger.info(f"Estatísticas atualizadas: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao atualizar estatísticas: {e}")
        raise
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=2)
def bulk_sync_orgaos(self, ufs: List[str] = None):
    """
    Sincroniza órgãos em lote por UF
    """
    try:
        logger.info(f"Sincronizando órgãos em lote para UFs: {ufs}")
        
        if not ufs:
            # Estados brasileiros
            ufs = [
                "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
                "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
                "RS", "RO", "RR", "SC", "SP", "SE", "TO"
            ]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        total_orgaos = 0
        
        for uf in ufs:
            try:
                result = loop.run_until_complete(
                    pncp_service.obter_orgaos(uf=uf, tamanho=100)
                )
                orgaos_uf = len(result.get("data", []))
                total_orgaos += orgaos_uf
                
                logger.info(f"Sincronizados {orgaos_uf} órgãos para {uf}")
                
                # Delay entre requisições para evitar rate limiting
                import time
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao sincronizar órgãos de {uf}: {e}")
                continue
        
        loop.close()
        
        result = {
            "total_orgaos": total_orgaos,
            "ufs_processadas": len(ufs)
        }
        
        logger.info(f"Sincronização de órgãos concluída: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Erro na sincronização em lote de órgãos: {e}")
        raise self.retry(exc=e, countdown=120)


# Tarefas de monitoramento
@celery_app.task
def health_check():
    """
    Verifica a saúde do sistema
    """
    try:
        # Verificar conexão com banco
        db = get_db()
        db.execute("SELECT 1")
        db.close()
        
        # Verificar conexão com Redis
        from app.core.cache import redis_client
        redis_client.ping()
        
        # Verificar conectividade com PNCP
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            modalidades = loop.run_until_complete(pncp_service.obter_modalidades())
            pncp_ok = len(modalidades) > 0
        except:
            pncp_ok = False
        
        loop.close()
        
        status = {
            "database": "ok",
            "redis": "ok",
            "pncp": "ok" if pncp_ok else "error",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Health check: {status}")
        return status
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Para executar o worker: celery -A app.tasks.sync_tasks worker --loglevel=info
    # Para executar o beat: celery -A app.tasks.sync_tasks beat --loglevel=info
    celery_app.start()
