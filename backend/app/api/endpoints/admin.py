"""
Endpoints para administração do sistema
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, date, timedelta
import json
import csv
import io

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.contrato import Usuario
from app.models.pca import PCA
from app.models.contratacao import Contratacao
from app.models.ata import Ata
from app.models.contrato import Contrato
from app.schemas.common import PaginatedResponse
from app.utils.helpers import paginate_query
from app.middleware.rate_limiting import limiter
from app.core.cache import get_cache, set_cache, clear_cache_pattern

router = APIRouter(prefix="/admin", tags=["Administração"])


@router.get("/dashboard")
@limiter.limit("100/minute")
async def obter_dashboard(
    request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém dados do dashboard administrativo
    """
    # Verificar permissões
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Verificar cache
    cache_key = "admin_dashboard"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    # Estatísticas gerais
    total_pcas = db.query(PCA).count()
    total_contratacoes = db.query(Contratacao).count()
    total_atas = db.query(Ata).count()
    total_contratos = db.query(Contrato).count()
    total_usuarios = db.query(Usuario).count()
    
    # Valor total dos contratos
    valor_total_contratos = db.query(
        func.sum(Contrato.valor_inicial)
    ).scalar() or 0
    
    # Estatísticas dos últimos 30 dias
    data_30_dias = datetime.now() - timedelta(days=30)
    
    pcas_30_dias = db.query(PCA).filter(PCA.created_at >= data_30_dias).count()
    contratacoes_30_dias = db.query(Contratacao).filter(
        Contratacao.created_at >= data_30_dias
    ).count()
    atas_30_dias = db.query(Ata).filter(Ata.created_at >= data_30_dias).count()
    contratos_30_dias = db.query(Contrato).filter(
        Contrato.created_at >= data_30_dias
    ).count()
    
    # Contratos próximos do vencimento
    data_90_dias = date.today() + timedelta(days=90)
    contratos_vencendo = db.query(Contrato).filter(
        Contrato.data_fim_vigencia <= data_90_dias,
        Contrato.situacao == "ATIVO"
    ).count()
    
    # Top 5 órgãos por valor de contratos
    top_orgaos = db.query(
        Contrato.orgao_nome,
        func.sum(Contrato.valor_inicial).label('valor_total'),
        func.count(Contrato.id).label('total_contratos')
    ).group_by(Contrato.orgao_nome).order_by(
        func.sum(Contrato.valor_inicial).desc()
    ).limit(5).all()
    
    # Estatísticas por modalidade
    stats_modalidade = db.query(
        Contratacao.modalidade,
        func.count(Contratacao.id).label('quantidade'),
        func.sum(Contratacao.valor_total_estimado).label('valor')
    ).group_by(Contratacao.modalidade).order_by(
        func.count(Contratacao.id).desc()
    ).limit(5).all()
    
    dashboard = {
        "totais": {
            "pcas": total_pcas,
            "contratacoes": total_contratacoes,
            "atas": total_atas,
            "contratos": total_contratos,
            "usuarios": total_usuarios,
            "valor_total_contratos": float(valor_total_contratos)
        },
        "ultimos_30_dias": {
            "pcas": pcas_30_dias,
            "contratacoes": contratacoes_30_dias,
            "atas": atas_30_dias,
            "contratos": contratos_30_dias
        },
        "alertas": {
            "contratos_vencendo": contratos_vencendo
        },
        "top_orgaos": [
            {
                "nome": orgao.orgao_nome,
                "valor_total": float(orgao.valor_total),
                "total_contratos": orgao.total_contratos
            }
            for orgao in top_orgaos
        ],
        "modalidades": [
            {
                "modalidade": mod.modalidade,
                "quantidade": mod.quantidade,
                "valor": float(mod.valor or 0)
            }
            for mod in stats_modalidade
        ]
    }
    
    # Cache por 15 minutos
    await set_cache(cache_key, dashboard, expire=900)
    
    return dashboard


@router.get("/logs")
@limiter.limit("50/minute")
async def obter_logs(
    request,
    level: Optional[str] = Query(None, description="Nível do log"),
    data_inicio: Optional[str] = Query(None, description="Data início"),
    data_fim: Optional[str] = Query(None, description="Data fim"),
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(50, ge=1, le=200, description="Tamanho da página"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém logs do sistema
    """
    # Verificar permissões
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Esta implementação seria completa com um modelo de logs
    # Por enquanto, retornar estrutura exemplo
    
    logs_exemplo = [
        {
            "id": 1,
            "timestamp": "2024-01-15T10:30:00",
            "level": "INFO",
            "message": "Usuário admin logado",
            "module": "auth",
            "user_id": current_user.id
        },
        {
            "id": 2,
            "timestamp": "2024-01-15T10:31:00",
            "level": "INFO",
            "message": "Sincronização PNCP iniciada",
            "module": "sync",
            "user_id": None
        }
    ]
    
    return {
        "data": logs_exemplo,
        "total": len(logs_exemplo),
        "page": page,
        "size": size,
        "pages": 1
    }


@router.get("/users")
@limiter.limit("50/minute")
async def listar_usuarios(
    request,
    ativo: Optional[bool] = Query(None, description="Status ativo"),
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista usuários do sistema
    """
    # Verificar permissões
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    query = db.query(Usuario)
    
    if ativo is not None:
        query = query.filter(Usuario.is_active == ativo)
    
    result = paginate_query(query, page, size)
    
    # Remover campos sensíveis
    for user in result["data"]:
        user.hashed_password = None
    
    return result


@router.put("/users/{user_id}/status")
@limiter.limit("10/minute")
async def alterar_status_usuario(
    request,
    user_id: int,
    ativo: bool = Query(..., description="Status ativo"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Altera status de um usuário
    """
    # Verificar permissões
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Não permitir desativar o próprio usuário
    if usuario.id == current_user.id and not ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível desativar o próprio usuário"
        )
    
    usuario.is_active = ativo
    db.commit()
    
    return {
        "message": f"Usuário {'ativado' if ativo else 'desativado'} com sucesso",
        "user_id": user_id,
        "is_active": ativo
    }


@router.post("/cache/clear")
@limiter.limit("5/minute")
async def limpar_cache(
    request,
    pattern: Optional[str] = Query(None, description="Padrão de chave"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Limpa cache do sistema
    """
    # Verificar permissões
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    if pattern:
        await clear_cache_pattern(pattern)
        message = f"Cache limpo para padrão: {pattern}"
    else:
        await clear_cache_pattern("*")
        message = "Todo o cache foi limpo"
    
    return {
        "message": message,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/sync/status")
@limiter.limit("30/minute")
async def obter_status_sincronizacao(
    request,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém status das sincronizações
    """
    # Verificar permissões
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Esta implementação seria completa com monitoramento de tasks
    # Por enquanto, retornar estrutura exemplo
    
    return {
        "ultima_sincronizacao": "2024-01-15T08:00:00",
        "proxima_sincronizacao": "2024-01-16T08:00:00",
        "status": "success",
        "registros_sincronizados": {
            "pcas": 150,
            "contratacoes": 300,
            "atas": 75,
            "contratos": 450
        },
        "erros": []
    }


@router.post("/sync/manual")
@limiter.limit("3/minute")
async def executar_sincronizacao_manual(
    request,
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Executa sincronização manual
    """
    # Verificar permissões
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Executar task de sincronização
    from app.tasks.sync_tasks import sync_pncp_data
    
    task = sync_pncp_data.delay(data_inicio, data_fim)
    
    return {
        "message": "Sincronização iniciada",
        "task_id": task.id,
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/export/data")
@limiter.limit("5/minute")
async def exportar_dados(
    request,
    formato: str = Query(..., description="Formato: csv, json, xlsx"),
    entidade: str = Query(..., description="Entidade: pca, contratacao, ata, contrato"),
    data_inicio: Optional[str] = Query(None, description="Data início"),
    data_fim: Optional[str] = Query(None, description="Data fim"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exporta dados do sistema
    """
    # Verificar permissões
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Validar parâmetros
    if formato not in ["csv", "json", "xlsx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato não suportado"
        )
    
    if entidade not in ["pca", "contratacao", "ata", "contrato"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entidade não suportada"
        )
    
    # Obter dados
    if entidade == "pca":
        query = db.query(PCA)
    elif entidade == "contratacao":
        query = db.query(Contratacao)
    elif entidade == "ata":
        query = db.query(Ata)
    elif entidade == "contrato":
        query = db.query(Contrato)
    
    # Aplicar filtros de data
    if data_inicio:
        data_inicio_obj = datetime.strptime(data_inicio, "%Y-%m-%d")
        query = query.filter(query.model.created_at >= data_inicio_obj)
    
    if data_fim:
        data_fim_obj = datetime.strptime(data_fim, "%Y-%m-%d")
        query = query.filter(query.model.created_at <= data_fim_obj)
    
    # Limitar exportação
    dados = query.limit(10000).all()
    
    if formato == "csv":
        return exportar_csv(dados, entidade)
    elif formato == "json":
        return exportar_json(dados, entidade)
    elif formato == "xlsx":
        return exportar_xlsx(dados, entidade)


@router.post("/backup")
@limiter.limit("2/minute")
async def criar_backup(
    request,
    incluir_arquivos: bool = Query(False, description="Incluir arquivos"),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cria backup do sistema
    """
    # Verificar permissões
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Esta implementação seria completa com sistema de backup
    # Por enquanto, retornar estrutura exemplo
    
    return {
        "message": "Backup iniciado",
        "backup_id": f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "incluir_arquivos": incluir_arquivos,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/system/health")
@limiter.limit("100/minute")
async def verificar_saude_sistema(
    request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verifica saúde do sistema
    """
    # Verificar permissões
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Verificar conexão com banco
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Verificar Redis
    try:
        from app.core.cache import redis_client
        redis_client.ping()
        cache_status = "healthy"
    except Exception as e:
        cache_status = f"error: {str(e)}"
    
    # Verificar PNCP
    try:
        from app.services.pncp_service import pncp_service
        import asyncio
        
        # Test com timeout
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        task = asyncio.wait_for(
            pncp_service.obter_modalidades(),
            timeout=10.0
        )
        
        modalidades = loop.run_until_complete(task)
        loop.close()
        
        pncp_status = "healthy" if modalidades else "error: empty response"
    except Exception as e:
        pncp_status = f"error: {str(e)}"
    
    # Verificar Celery
    try:
        from app.tasks.sync_tasks import celery_app
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        celery_status = "healthy" if active_tasks is not None else "error: no workers"
    except Exception as e:
        celery_status = f"error: {str(e)}"
    
    return {
        "database": db_status,
        "cache": cache_status,
        "pncp": pncp_status,
        "celery": celery_status,
        "timestamp": datetime.now().isoformat()
    }


def exportar_csv(dados, entidade):
    """
    Exporta dados em formato CSV
    """
    from fastapi.responses import StreamingResponse
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escrever cabeçalho
    if dados:
        headers = [column.name for column in dados[0].__table__.columns]
        writer.writerow(headers)
        
        # Escrever dados
        for item in dados:
            row = [getattr(item, header) for header in headers]
            writer.writerow(row)
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={entidade}_export.csv"}
    )


def exportar_json(dados, entidade):
    """
    Exporta dados em formato JSON
    """
    from fastapi.responses import JSONResponse
    
    dados_json = []
    for item in dados:
        item_dict = {}
        for column in item.__table__.columns:
            value = getattr(item, column.name)
            if isinstance(value, (datetime, date)):
                value = value.isoformat()
            item_dict[column.name] = value
        dados_json.append(item_dict)
    
    return JSONResponse(
        content=dados_json,
        headers={"Content-Disposition": f"attachment; filename={entidade}_export.json"}
    )


def exportar_xlsx(dados, entidade):
    """
    Exporta dados em formato Excel
    """
    # Implementação com pandas e openpyxl
    # Por enquanto, retornar erro
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Exportação Excel não implementada"
    )
