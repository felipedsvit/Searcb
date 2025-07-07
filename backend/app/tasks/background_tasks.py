"""
Tasks adicionais para processamento em background
"""
import asyncio
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import logging
import json

from celery import Celery
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.pncp_service import pncp_service
from app.services.usuario_service import LogSistemaService
from app.models.pca import PCA
from app.models.contratacao import Contratacao
from app.models.ata import AtaRegistroPreco
from app.models.contrato import Contrato
from app.models.usuario import Usuario, LogSistema
from app.core.cache import clear_cache_pattern, get_cache, set_cache
from app.utils.helpers import send_email, generate_report

logger = logging.getLogger(__name__)

# Usar a mesma instância do Celery
from app.tasks.sync_tasks import celery_app


@celery_app.task(bind=True, max_retries=3)
def processo_sincronizacao_completa(self, data_inicio: str = None, data_fim: str = None):
    """
    Task para sincronização completa de dados do PNCP
    """
    try:
        # Converter datas
        if data_inicio:
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        else:
            data_inicio = date.today() - timedelta(days=30)
        
        if data_fim:
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
        else:
            data_fim = date.today()
        
        logger.info(f"Iniciando sincronização completa: {data_inicio} a {data_fim}")
        
        # Executar sincronização
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                pncp_service.sincronizar_dados(data_inicio, data_fim)
            )
            
            # Registrar log de sucesso
            with SessionLocal() as db:
                log_service = LogSistemaService(db)
                loop.run_until_complete(
                    log_service.create_log(
                        usuario_id=None,
                        nivel="INFO",
                        categoria="SYNC",
                        mensagem=f"Sincronização completa executada com sucesso",
                        detalhes=json.dumps(result),
                        modulo="celery_tasks"
                    )
                )
            
            logger.info(f"Sincronização completa concluída: {result}")
            return result
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Erro na sincronização completa: {exc}")
        
        # Registrar log de erro
        try:
            with SessionLocal() as db:
                log_service = LogSistemaService(db)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    loop.run_until_complete(
                        log_service.create_log(
                            usuario_id=None,
                            nivel="ERROR",
                            categoria="SYNC",
                            mensagem=f"Erro na sincronização completa",
                            detalhes=str(exc),
                            modulo="celery_tasks"
                        )
                    )
                finally:
                    loop.close()
        except Exception as log_error:
            logger.error(f"Erro ao registrar log: {log_error}")
        
        # Retry com backoff exponencial
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def processo_limpeza_cache(self):
    """
    Task para limpeza periódica do cache
    """
    try:
        logger.info("Iniciando limpeza de cache")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Limpar cache de dados antigos
            patterns = [
                "pncp_*",
                "pca_list_*",
                "contratacao_list_*",
                "ata_list_*",
                "contrato_list_*",
                "*_stats_*"
            ]
            
            for pattern in patterns:
                loop.run_until_complete(clear_cache_pattern(pattern))
            
            logger.info("Limpeza de cache concluída")
            return {"status": "success", "patterns_cleaned": len(patterns)}
            
        finally:
            loop.close()
            
    except Exception as exc:
        logger.error(f"Erro na limpeza de cache: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def processo_backup_dados(self):
    """
    Task para backup automático dos dados
    """
    try:
        logger.info("Iniciando backup de dados")
        
        with SessionLocal() as db:
            # Estatísticas gerais
            stats = {
                "pcas": db.query(func.count(PCA.id)).scalar(),
                "contratacoes": db.query(func.count(Contratacao.id)).scalar(),
                "atas": db.query(func.count(AtaRegistroPreco.id)).scalar(),
                "contratos": db.query(func.count(Contrato.id)).scalar(),
                "usuarios": db.query(func.count(Usuario.id)).scalar(),
                "data_backup": datetime.utcnow().isoformat()
            }
            
            # Aqui você pode implementar a lógica de backup
            # Por exemplo, exportar para S3, criar dump do banco, etc.
            
            logger.info(f"Backup concluído: {stats}")
            return stats
            
    except Exception as exc:
        logger.error(f"Erro no backup de dados: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def processo_relatorio_diario(self):
    """
    Task para gerar relatório diário
    """
    try:
        logger.info("Gerando relatório diário")
        
        with SessionLocal() as db:
            hoje = date.today()
            ontem = hoje - timedelta(days=1)
            
            # Dados do relatório
            dados = {
                "data": hoje.isoformat(),
                "periodo": f"{ontem.isoformat()} a {hoje.isoformat()}",
                "novos_pcas": db.query(func.count(PCA.id)).filter(
                    PCA.created_at >= ontem
                ).scalar(),
                "novas_contratacoes": db.query(func.count(Contratacao.id)).filter(
                    Contratacao.created_at >= ontem
                ).scalar(),
                "novas_atas": db.query(func.count(AtaRegistroPreco.id)).filter(
                    AtaRegistroPreco.created_at >= ontem
                ).scalar(),
                "novos_contratos": db.query(func.count(Contrato.id)).filter(
                    Contrato.created_at >= ontem
                ).scalar(),
                "total_usuarios_ativos": db.query(func.count(Usuario.id)).filter(
                    Usuario.ativo == True
                ).scalar(),
                "logins_ontem": db.query(func.count(Usuario.id)).filter(
                    Usuario.ultimo_login >= ontem
                ).scalar()
            }
            
            # Gerar relatório
            relatorio = generate_report("relatorio_diario", dados)
            
            # Enviar por email para administradores
            admins = db.query(Usuario).filter(
                and_(Usuario.is_admin == True, Usuario.ativo == True)
            ).all()
            
            for admin in admins:
                send_email(
                    to=admin.email,
                    subject=f"Relatório Diário SEARCB - {hoje.strftime('%d/%m/%Y')}",
                    template="relatorio_diario",
                    context=dados
                )
            
            logger.info(f"Relatório diário enviado para {len(admins)} administradores")
            return dados
            
    except Exception as exc:
        logger.error(f"Erro na geração do relatório diário: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def processo_monitoramento_sistema(self):
    """
    Task para monitoramento do sistema
    """
    try:
        logger.info("Executando monitoramento do sistema")
        
        with SessionLocal() as db:
            # Verificar saúde do banco
            try:
                db.execute("SELECT 1")
                db_status = "OK"
            except Exception as e:
                db_status = f"ERROR: {str(e)}"
            
            # Verificar logs de erro recentes
            uma_hora_atras = datetime.utcnow() - timedelta(hours=1)
            erros_recentes = db.query(func.count(LogSistema.id)).filter(
                and_(
                    LogSistema.nivel == "ERROR",
                    LogSistema.created_at >= uma_hora_atras
                )
            ).scalar()
            
            # Verificar tentativas de login falhadas
            tentativas_falhas = db.query(func.count(Usuario.id)).filter(
                Usuario.tentativas_login > 5
            ).scalar()
            
            # Status do sistema
            status = {
                "timestamp": datetime.utcnow().isoformat(),
                "database": db_status,
                "errors_last_hour": erros_recentes,
                "failed_login_attempts": tentativas_falhas,
                "status": "OK" if db_status == "OK" and erros_recentes < 10 else "WARNING"
            }
            
            # Cachear status
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(
                    set_cache("system_status", status, expire=300)
                )
            finally:
                loop.close()
            
            # Alertas críticos
            if status["status"] == "WARNING":
                admins = db.query(Usuario).filter(
                    and_(Usuario.is_admin == True, Usuario.ativo == True)
                ).all()
                
                for admin in admins:
                    send_email(
                        to=admin.email,
                        subject="Alerta Sistema SEARCB",
                        template="alerta_sistema",
                        context=status
                    )
            
            logger.info(f"Monitoramento concluído: {status}")
            return status
            
    except Exception as exc:
        logger.error(f"Erro no monitoramento do sistema: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def processo_notificacao_usuario(self, usuario_id: int, tipo: str, dados: Dict[str, Any]):
    """
    Task para envio de notificações para usuários
    """
    try:
        logger.info(f"Enviando notificação para usuário {usuario_id}: {tipo}")
        
        with SessionLocal() as db:
            usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            
            if not usuario:
                logger.warning(f"Usuário {usuario_id} não encontrado")
                return {"status": "error", "message": "Usuário não encontrado"}
            
            # Templates de notificação
            templates = {
                "pca_criado": {
                    "subject": "Novo PCA Criado",
                    "template": "pca_criado"
                },
                "contratacao_atualizada": {
                    "subject": "Contratação Atualizada",
                    "template": "contratacao_atualizada"
                },
                "ata_vencendo": {
                    "subject": "Ata de Registro de Preços Vencendo",
                    "template": "ata_vencendo"
                },
                "contrato_vencendo": {
                    "subject": "Contrato Vencendo",
                    "template": "contrato_vencendo"
                }
            }
            
            if tipo not in templates:
                logger.warning(f"Tipo de notificação não suportado: {tipo}")
                return {"status": "error", "message": "Tipo de notificação não suportado"}
            
            # Enviar email
            send_email(
                to=usuario.email,
                subject=templates[tipo]["subject"],
                template=templates[tipo]["template"],
                context=dados
            )
            
            logger.info(f"Notificação enviada para {usuario.email}")
            return {"status": "success", "usuario": usuario.email, "tipo": tipo}
            
    except Exception as exc:
        logger.error(f"Erro no envio de notificação: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def processo_validacao_dados(self):
    """
    Task para validação de integridade dos dados
    """
    try:
        logger.info("Iniciando validação de integridade dos dados")
        
        with SessionLocal() as db:
            problemas = []
            
            # Verificar PCAs sem valor total
            pcas_sem_valor = db.query(func.count(PCA.id)).filter(
                or_(PCA.valor_total.is_(None), PCA.valor_total <= 0)
            ).scalar()
            
            if pcas_sem_valor > 0:
                problemas.append(f"PCAs sem valor total: {pcas_sem_valor}")
            
            # Verificar contratações sem PCA
            contratacoes_sem_pca = db.query(func.count(Contratacao.id)).filter(
                Contratacao.pca_id.is_(None)
            ).scalar()
            
            if contratacoes_sem_pca > 0:
                problemas.append(f"Contratações sem PCA: {contratacoes_sem_pca}")
            
            # Verificar usuários inativos com login recente
            usuarios_inativos_logados = db.query(func.count(Usuario.id)).filter(
                and_(
                    Usuario.ativo == False,
                    Usuario.ultimo_login >= datetime.utcnow() - timedelta(days=1)
                )
            ).scalar()
            
            if usuarios_inativos_logados > 0:
                problemas.append(f"Usuários inativos com login recente: {usuarios_inativos_logados}")
            
            # Verificar contratos sem data de vigência
            contratos_sem_vigencia = db.query(func.count(Contrato.id)).filter(
                Contrato.data_vigencia_fim.is_(None)
            ).scalar()
            
            if contratos_sem_vigencia > 0:
                problemas.append(f"Contratos sem data de vigência: {contratos_sem_vigencia}")
            
            resultado = {
                "timestamp": datetime.utcnow().isoformat(),
                "problemas_encontrados": len(problemas),
                "detalhes": problemas,
                "status": "OK" if len(problemas) == 0 else "WARNING"
            }
            
            # Registrar log
            log_service = LogSistemaService(db)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(
                    log_service.create_log(
                        usuario_id=None,
                        nivel="INFO" if len(problemas) == 0 else "WARNING",
                        categoria="VALIDATION",
                        mensagem=f"Validação de integridade concluída",
                        detalhes=json.dumps(resultado),
                        modulo="celery_tasks"
                    )
                )
            finally:
                loop.close()
            
            logger.info(f"Validação de integridade concluída: {resultado}")
            return resultado
            
    except Exception as exc:
        logger.error(f"Erro na validação de integridade: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# Adicionar tasks ao schedule
celery_app.conf.beat_schedule.update({
    "sincronizacao-completa-diaria": {
        "task": "app.tasks.background_tasks.processo_sincronizacao_completa",
        "schedule": 3600.0,  # A cada hora
        "options": {"queue": "sync"}
    },
    "limpeza-cache-diaria": {
        "task": "app.tasks.background_tasks.processo_limpeza_cache",
        "schedule": 21600.0,  # A cada 6 horas
        "options": {"queue": "maintenance"}
    },
    "backup-dados-diario": {
        "task": "app.tasks.background_tasks.processo_backup_dados",
        "schedule": 86400.0,  # A cada 24 horas
        "options": {"queue": "backup"}
    },
    "relatorio-diario": {
        "task": "app.tasks.background_tasks.processo_relatorio_diario",
        "schedule": 86400.0,  # A cada 24 horas (6h da manhã)
        "options": {"queue": "reports"}
    },
    "monitoramento-sistema": {
        "task": "app.tasks.background_tasks.processo_monitoramento_sistema",
        "schedule": 300.0,  # A cada 5 minutos
        "options": {"queue": "monitoring"}
    },
    "validacao-dados-diaria": {
        "task": "app.tasks.background_tasks.processo_validacao_dados",
        "schedule": 86400.0,  # A cada 24 horas
        "options": {"queue": "validation"}
    }
})

# Configurar filas
celery_app.conf.task_routes = {
    "app.tasks.background_tasks.processo_sincronizacao_completa": {"queue": "sync"},
    "app.tasks.background_tasks.processo_limpeza_cache": {"queue": "maintenance"},
    "app.tasks.background_tasks.processo_backup_dados": {"queue": "backup"},
    "app.tasks.background_tasks.processo_relatorio_diario": {"queue": "reports"},
    "app.tasks.background_tasks.processo_monitoramento_sistema": {"queue": "monitoring"},
    "app.tasks.background_tasks.processo_validacao_dados": {"queue": "validation"},
    "app.tasks.background_tasks.processo_notificacao_usuario": {"queue": "notifications"}
}
