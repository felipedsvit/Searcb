"""
Endpoints para gestão de Webhooks
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import json
import hmac
import hashlib
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.schemas.common import PaginatedResponse
from app.utils.helpers import paginate_query
from app.middleware.rate_limiting import limiter
from app.core.cache import get_cache, set_cache
from app.core.config import settings

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


# Modelo para webhook (seria criado em models/webhook.py)
class WebhookEvent:
    def __init__(self, event_type: str, data: Dict[str, Any], timestamp: datetime = None):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.now()


@router.post("/pncp/notification")
@limiter.limit("100/minute")
async def receber_notificacao_pncp(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Recebe notificações do PNCP via webhook
    """
    try:
        # Obter o corpo da requisição
        body = await request.body()
        payload = json.loads(body.decode())
        
        # Verificar assinatura se configurada
        if hasattr(settings, 'PNCP_WEBHOOK_SECRET') and settings.PNCP_WEBHOOK_SECRET:
            signature = request.headers.get('X-PNCP-Signature')
            if not signature:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Assinatura do webhook não fornecida"
                )
            
            expected_signature = hmac.new(
                settings.PNCP_WEBHOOK_SECRET.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, f"sha256={expected_signature}"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Assinatura do webhook inválida"
                )
        
        # Processar evento
        event_type = payload.get('event_type')
        event_data = payload.get('data', {})
        
        # Log do evento
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Webhook PNCP recebido: {event_type}")
        
        # Processar diferentes tipos de eventos
        if event_type == 'pca.created':
            await processar_pca_criado(event_data, db)
        elif event_type == 'pca.updated':
            await processar_pca_atualizado(event_data, db)
        elif event_type == 'contratacao.created':
            await processar_contratacao_criada(event_data, db)
        elif event_type == 'contratacao.updated':
            await processar_contratacao_atualizada(event_data, db)
        elif event_type == 'ata.created':
            await processar_ata_criada(event_data, db)
        elif event_type == 'ata.updated':
            await processar_ata_atualizada(event_data, db)
        elif event_type == 'contrato.created':
            await processar_contrato_criado(event_data, db)
        elif event_type == 'contrato.updated':
            await processar_contrato_atualizado(event_data, db)
        else:
            logger.warning(f"Tipo de evento não reconhecido: {event_type}")
        
        return {
            "status": "success",
            "message": "Webhook processado com sucesso",
            "event_type": event_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload JSON inválido"
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao processar webhook PNCP: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar webhook"
        )


@router.post("/interno/notification")
@limiter.limit("1000/minute")
async def receber_notificacao_interna(
    request: Request,
    event: Dict[str, Any],
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Recebe notificações internas do sistema
    """
    try:
        event_type = event.get('type')
        event_data = event.get('data', {})
        
        # Log do evento
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Evento interno recebido: {event_type} por usuário {current_user.id}")
        
        # Processar diferentes tipos de eventos internos
        if event_type == 'user.login':
            await processar_login_usuario(event_data, current_user, db)
        elif event_type == 'user.logout':
            await processar_logout_usuario(event_data, current_user, db)
        elif event_type == 'data.export':
            await processar_exportacao_dados(event_data, current_user, db)
        elif event_type == 'system.backup':
            await processar_backup_sistema(event_data, current_user, db)
        elif event_type == 'alert.contract_expiry':
            await processar_alerta_vencimento(event_data, current_user, db)
        else:
            logger.warning(f"Tipo de evento interno não reconhecido: {event_type}")
        
        return {
            "status": "success",
            "message": "Evento interno processado com sucesso",
            "event_type": event_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao processar evento interno: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar evento"
        )


@router.get("/events")
@limiter.limit("100/minute")
async def listar_eventos(
    request: Request,
    event_type: Optional[str] = Query(None, description="Tipo de evento"),
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista eventos de webhook processados
    """
    # Verificar permissões
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Esta implementação seria completa com um modelo de webhook_events
    # Por enquanto, retornar estrutura exemplo
    
    eventos_exemplo = [
        {
            "id": 1,
            "event_type": "pca.created",
            "data": {"pca_id": "123", "orgao_cnpj": "12345678000100"},
            "timestamp": "2024-01-15T10:30:00",
            "status": "processed"
        },
        {
            "id": 2,
            "event_type": "contratacao.updated",
            "data": {"contratacao_id": "456", "situacao": "HOMOLOGADO"},
            "timestamp": "2024-01-15T11:45:00",
            "status": "processed"
        }
    ]
    
    return {
        "data": eventos_exemplo,
        "total": len(eventos_exemplo),
        "page": page,
        "size": size,
        "pages": 1
    }


@router.post("/test")
@limiter.limit("10/minute")
async def testar_webhook(
    request: Request,
    event_type: str = Query(..., description="Tipo de evento para teste"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Testa processamento de webhook
    """
    # Verificar permissões
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Dados de teste baseados no tipo de evento
    test_data = {
        "pca.created": {
            "pca_id": "test_pca_123",
            "orgao_cnpj": "12345678000100",
            "ano": 2024,
            "valor_total": 1000000.00
        },
        "contratacao.created": {
            "contratacao_id": "test_contratacao_456",
            "numero_compra": "TEST-2024-001",
            "modalidade": "PREGAO_ELETRONICO",
            "situacao": "ABERTA"
        },
        "ata.created": {
            "ata_id": "test_ata_789",
            "numero_ata": "ATA-TEST-2024-001",
            "data_publicacao": "2024-01-15"
        },
        "contrato.created": {
            "contrato_id": "test_contrato_101",
            "numero_contrato": "CONT-TEST-2024-001",
            "fornecedor_cnpj": "98765432000100",
            "valor_inicial": 50000.00
        }
    }
    
    if event_type not in test_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de evento não suportado: {event_type}"
        )
    
    # Simular processamento
    event_data = test_data[event_type]
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Teste de webhook: {event_type} com dados: {event_data}")
    
    return {
        "status": "success",
        "message": f"Teste de webhook {event_type} executado com sucesso",
        "event_type": event_type,
        "test_data": event_data,
        "timestamp": datetime.now().isoformat()
    }


# Funções de processamento de eventos
async def processar_pca_criado(data: Dict[str, Any], db: Session):
    """
    Processa evento de PCA criado
    """
    from app.models.pca import PCA
    from app.services.pncp_service import pncp_service
    
    pca_id = data.get('pca_id')
    if not pca_id:
        return
    
    try:
        # Buscar dados completos do PCA no PNCP
        pca_data = await pncp_service.obter_pca_por_id(pca_id)
        
        # Verificar se já existe no banco
        existing_pca = db.query(PCA).filter(PCA.pncp_id == pca_id).first()
        if existing_pca:
            return
        
        # Criar novo PCA
        pca = PCA(
            pncp_id=pca_id,
            orgao_cnpj=pca_data.get('orgao_cnpj'),
            orgao_nome=pca_data.get('orgao_nome'),
            ano=pca_data.get('ano'),
            valor_total=pca_data.get('valor_total', 0),
            # Adicionar outros campos conforme necessário
        )
        
        db.add(pca)
        db.commit()
        
        # Invalidar cache
        from app.core.cache import clear_cache_pattern
        await clear_cache_pattern("pca_*")
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao processar PCA criado: {e}")


async def processar_pca_atualizado(data: Dict[str, Any], db: Session):
    """
    Processa evento de PCA atualizado
    """
    # Implementação similar ao PCA criado
    pass


async def processar_contratacao_criada(data: Dict[str, Any], db: Session):
    """
    Processa evento de contratação criada
    """
    # Implementação similar
    pass


async def processar_contratacao_atualizada(data: Dict[str, Any], db: Session):
    """
    Processa evento de contratação atualizada
    """
    # Implementação similar
    pass


async def processar_ata_criada(data: Dict[str, Any], db: Session):
    """
    Processa evento de ata criada
    """
    # Implementação similar
    pass


async def processar_ata_atualizada(data: Dict[str, Any], db: Session):
    """
    Processa evento de ata atualizada
    """
    # Implementação similar
    pass


async def processar_contrato_criado(data: Dict[str, Any], db: Session):
    """
    Processa evento de contrato criado
    """
    # Implementação similar
    pass


async def processar_contrato_atualizado(data: Dict[str, Any], db: Session):
    """
    Processa evento de contrato atualizado
    """
    # Implementação similar
    pass


async def processar_login_usuario(data: Dict[str, Any], usuario: Usuario, db: Session):
    """
    Processa evento de login de usuário
    """
    # Log de auditoria, atualizar último login, etc.
    pass


async def processar_logout_usuario(data: Dict[str, Any], usuario: Usuario, db: Session):
    """
    Processa evento de logout de usuário
    """
    # Log de auditoria
    pass


async def processar_exportacao_dados(data: Dict[str, Any], usuario: Usuario, db: Session):
    """
    Processa evento de exportação de dados
    """
    # Log de auditoria, controle de acesso
    pass


async def processar_backup_sistema(data: Dict[str, Any], usuario: Usuario, db: Session):
    """
    Processa evento de backup do sistema
    """
    # Log de auditoria
    pass


async def processar_alerta_vencimento(data: Dict[str, Any], usuario: Usuario, db: Session):
    """
    Processa alerta de vencimento de contrato
    """
    # Enviar notificações, emails, etc.
    pass
