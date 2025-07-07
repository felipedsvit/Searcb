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
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.models.pca import PCA
from app.models.contratacao import Contratacao
from app.models.ata import AtaRegistroPreco
from app.models.contrato import Contrato
from app.schemas.common import PaginatedResponse
from app.utils.helpers import paginate_query
from app.middleware.rate_limiting import limiter
from app.core.cache import get_cache, set_cache, clear_cache_pattern

router = APIRouter(tags=["Administração"])


@router.get("/dashboard")
async def obter_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém dados do dashboard administrativo
    """
    # Fetch user from database to check admin status
    user_id = current_user.get("sub")
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo ou não encontrado"
        )
    
    # Verificar permissões
    if not user.is_admin:
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
    total_atas = db.query(AtaRegistroPreco).count()
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
    atas_30_dias = db.query(AtaRegistroPreco).filter(AtaRegistroPreco.created_at >= data_30_dias).count()
    contratos_30_dias = db.query(Contrato).filter(
        Contrato.created_at >= data_30_dias
    ).count()
    
    # Contratos próximos do vencimento
    data_90_dias = date.today() + timedelta(days=90)
    contratos_vencendo = db.query(Contrato).filter(
        Contrato.data_vigencia_fim <= data_90_dias,
        Contrato.situacao_contrato == "ATIVO"
    ).count()
    
    # Top 5 órgãos por valor de contratos
    top_orgaos = db.query(
        Contrato.orgao_entidade_razao_social,
        func.sum(Contrato.valor_inicial).label('valor_total'),
        func.count(Contrato.id).label('total_contratos')
    ).group_by(Contrato.orgao_entidade_razao_social).order_by(
        func.sum(Contrato.valor_inicial).desc()
    ).limit(5).all()
    
    # Estatísticas por modalidade
    stats_modalidade = db.query(
        Contratacao.modalidade_nome,
        func.count(Contratacao.id).label('quantidade'),
        func.sum(Contratacao.valor_total_estimado).label('valor')
    ).group_by(Contratacao.modalidade_nome).order_by(
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
                "nome": orgao.orgao_entidade_razao_social,
                "valor_total": float(orgao.valor_total),
                "total_contratos": orgao.total_contratos
            }
            for orgao in top_orgaos
        ],
        "modalidades": [
            {
                "modalidade": mod.modalidade_nome,
                "quantidade": mod.quantidade,
                "valor": float(mod.valor or 0)
            }
            for mod in stats_modalidade
        ]
    }
    
    # Cache por 15 minutos
    await set_cache(cache_key, dashboard, ttl=900)
    
    return dashboard


@router.get("/logs")
async def listar_logs(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(50, ge=1, le=200, description="Tamanho da página"),
    nivel: Optional[str] = Query(None, description="Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    modulo: Optional[str] = Query(None, description="Módulo/arquivo de origem"),
    categoria: Optional[str] = Query(None, description="Categoria do log"),
    data_inicio: Optional[date] = Query(None, description="Data de início (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data de fim (YYYY-MM-DD)"),
    termo_busca: Optional[str] = Query(None, description="Termo de busca na mensagem"),
    usuario_id: Optional[int] = Query(None, description="ID do usuário"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista logs do sistema com filtros e paginação
    
    Requer permissão de administrador
    """
    # Fetch user from database to check admin status
    user_id = current_user.get("sub")
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo ou não encontrado"
        )
    
    # Verificar permissões
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Importar modelo de logs
    from app.models.usuario import LogSistema
    
    # Construir query base
    query = db.query(LogSistema)
    
    # Aplicar filtros
    if nivel:
        query = query.filter(LogSistema.nivel == nivel.upper())
    
    if modulo:
        query = query.filter(LogSistema.modulo.ilike(f"%{modulo}%"))
        
    if categoria:
        query = query.filter(LogSistema.categoria.ilike(f"%{categoria}%"))
    
    if data_inicio:
        query = query.filter(LogSistema.created_at >= data_inicio)
    
    if data_fim:
        query = query.filter(LogSistema.created_at <= data_fim)
    
    if termo_busca:
        query = query.filter(LogSistema.mensagem.ilike(f"%{termo_busca}%"))
        
    if usuario_id:
        query = query.filter(LogSistema.usuario_id == usuario_id)
    
    # Ordenar por timestamp decrescente
    query = query.order_by(LogSistema.created_at.desc())
    
    # Contar total
    total = query.count()
    
    # Aplicar paginação
    skip = (page - 1) * size
    logs = query.offset(skip).limit(size).all()
    
    # Paginar
    result = paginate_query(query, page, size)
    
    return {
        "data": [
            {
                "id": log.id,
                "nivel": log.nivel,
                "categoria": log.categoria,
                "modulo": log.modulo,
                "mensagem": log.mensagem,
                "detalhes": log.detalhes,
                "ip_origem": log.ip_origem,
                "user_agent": log.user_agent,
                "endpoint": log.endpoint,
                "metodo_http": log.metodo_http,
                "tempo_processamento": log.tempo_processamento,
                "status_code": log.status_code,
                "contexto_adicional": log.contexto_adicional,
                "usuario_id": log.usuario_id,
                "timestamp": log.created_at,
                "updated_at": log.updated_at
            } for log in logs
        ],
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.get("/users")
async def listar_usuarios(
    ativo: Optional[bool] = Query(None, description="Status ativo"),
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista usuários do sistema
    """
    # Fetch user from database to check admin status
    user_id = current_user.get("sub")
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo ou não encontrado"
        )
    
    # Verificar permissões
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    query = db.query(Usuario)
    
    if ativo is not None:
        query = query.filter(Usuario.ativo == ativo)
    
    result = paginate_query(query, page, size)
    
    # Remover campos sensíveis
    for user in result["data"]:
        user.hashed_password = None
    
    return result


@router.put("/users/{user_id}/status")
async def alterar_status_usuario(
    user_id: int,
    ativo: bool = Query(..., description="Status ativo"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Altera status de um usuário
    """
    # Fetch user from database to check admin status
    admin_user_id = current_user.get("sub")
    admin_user = db.query(Usuario).filter(Usuario.id == int(admin_user_id)).first()
    if not admin_user or not admin_user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo ou não encontrado"
        )
    
    # Verificar permissões
    if not admin_user.is_admin:
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
    if usuario.id == admin_user.id and not ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível desativar o próprio usuário"
        )
    
    usuario.ativo = ativo
    db.commit()
    
    return {
        "message": f"Usuário {'ativado' if ativo else 'desativado'} com sucesso",
        "user_id": user_id,
        "ativo": ativo
    }


@router.post("/cache/clear")
async def limpar_cache(
    pattern: Optional[str] = Query(None, description="Padrão de chave"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Limpa cache do sistema
    """
    # Fetch user from database to check admin status
    user_id = current_user.get("sub")
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo ou não encontrado"
        )
    
    # Verificar permissões
    if not user.is_admin:
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
async def obter_status_sincronizacao(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém status das sincronizações
    """
    # Fetch user from database to check admin status
    user_id = current_user.get("sub")
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo ou não encontrado"
        )
    
    # Verificar permissões
    if not user.is_admin:
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
async def executar_sincronizacao_manual(
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executa sincronização manual
    """
    # Fetch user from database to check admin status
    user_id = current_user.get("sub")
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo ou não encontrado"
        )
    
    # Verificar permissões
    if not user.is_admin:
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
async def exportar_dados(
    formato: str = Query(..., description="Formato: csv, json, xlsx"),
    entidade: str = Query(..., description="Entidade: pca, contratacao, ata, contrato"),
    data_inicio: Optional[str] = Query(None, description="Data início"),
    data_fim: Optional[str] = Query(None, description="Data fim"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exporta dados do sistema
    """
    # Fetch user from database to check admin status
    user_id = current_user.get("sub")
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo ou não encontrado"
        )
    
    # Verificar permissões
    if not user.is_admin:
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
        query = db.query(AtaRegistroPreco)
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
async def criar_backup(
    incluir_arquivos: bool = Query(False, description="Incluir arquivos"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria backup do sistema
    """
    # Fetch user from database to check admin status
    user_id = current_user.get("sub")
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo ou não encontrado"
        )
    
    # Verificar permissões
    if not user.is_admin:
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
async def verificar_saude_sistema(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verifica saúde do sistema
    """
    # Fetch user from database to check admin status
    user_id = current_user.get("sub")
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo ou não encontrado"
        )
    
    # Verificar permissões
    if not user.is_admin:
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


# Endpoints de Configurações do Sistema

@router.get("/configuracoes")
async def listar_configuracoes(
    categoria: Optional[str] = Query(None, description="Categoria das configurações"),
    ativo: Optional[bool] = Query(None, description="Filtrar por configurações ativas"),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(50, ge=1, le=200, description="Tamanho da página"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista configurações do sistema
    
    Requer permissão de administrador
    """
    # Fetch user from database to check admin status
    user_id = current_user.get("sub")
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo ou não encontrado"
        )
    
    # Verificar permissões
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Verificar cache
    cache_key = f"configuracoes_{categoria or 'all'}_{ativo}_{page}_{size}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    # Importar modelo de configurações
    from app.models.usuario import ConfiguracaoSistema
    
    # Construir query
    query = db.query(ConfiguracaoSistema)
    
    if categoria:
        query = query.filter(ConfiguracaoSistema.categoria == categoria)
        
    if ativo is not None:
        query = query.filter(ConfiguracaoSistema.ativo == ativo)
    
    # Ordenar por categoria e chave
    query = query.order_by(ConfiguracaoSistema.categoria, ConfiguracaoSistema.chave)
    
    # Contar total
    total = query.count()
    
    # Aplicar paginação
    skip = (page - 1) * size
    configuracoes = query.offset(skip).limit(size).all()
    
    # Agrupar por categoria se não foi especificada uma categoria
    if not categoria:
        result = {}
        for config in configuracoes:
            if config.categoria not in result:
                result[config.categoria] = []
            
            result[config.categoria].append({
                "id": config.id,
                "chave": config.chave,
                "valor": config.valor,
                "descricao": config.descricao,
                "tipo": config.tipo,
                "ativo": config.ativo,
                "somente_leitura": config.somente_leitura,
                "valor_padrao": config.valor_padrao,
                "valor_minimo": config.valor_minimo,
                "valor_maximo": config.valor_maximo,
                "ultima_atualizacao": config.updated_at
            })
        
        response = {
            "data": result,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    else:
        response = {
            "data": [
                {
                    "id": config.id,
                    "chave": config.chave,
                    "valor": config.valor,
                    "descricao": config.descricao,
                    "tipo": config.tipo,
                    "ativo": config.ativo,
                    "somente_leitura": config.somente_leitura,
                    "valor_padrao": config.valor_padrao,
                    "valor_minimo": config.valor_minimo,
                    "valor_maximo": config.valor_maximo,
                    "ultima_atualizacao": config.updated_at
                } for config in configuracoes
            ],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    # Cache por 1 hora
    await set_cache(cache_key, response, ttl=3600)
    
    return response


@router.put("/configuracoes/{chave}")
async def atualizar_configuracao(
    chave: str,
    valor: str = Query(..., description="Novo valor da configuração"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza configuração específica
    
    Requer permissão de administrador
    """
    # Fetch user from database to check admin status
    user_id = current_user.get("sub")
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not user or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo ou não encontrado"
        )
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Importar modelo de configurações
    from app.models.usuario import ConfiguracaoSistema
    
    # Buscar configuração
    config = db.query(ConfiguracaoSistema).filter(
        ConfiguracaoSistema.chave == chave
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração não encontrada"
        )
    
    if config.somente_leitura:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta configuração é somente leitura"
        )
    
    # Validar tipo do valor
    if not validar_tipo_configuracao(valor, config.tipo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Valor inválido para o tipo {config.tipo}"
        )
    
    # Atualizar configuração
    config.valor = valor
    config.updated_at = datetime.now()
    
    db.commit()
    
    # Invalidar cache
    await clear_cache_pattern("configuracoes_*")
    
    # Log da alteração
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Configuração {chave} atualizada por usuário {user.username}")
    
    return {
        "status": "success",
        "message": "Configuração atualizada com sucesso",
        "chave": chave,
        "valor": valor
    }


def validar_tipo_configuracao(valor: str, tipo: str) -> bool:
    """
    Valida se o valor é compatível com o tipo da configuração
    """
    try:
        if tipo == "INTEGER":
            int(valor)
        elif tipo == "BOOLEAN":
            if valor.lower() not in ["true", "false", "1", "0"]:
                return False
        elif tipo == "STRING":
            # String sempre é válida
            pass
        elif tipo == "JSON":
            import json
            json.loads(valor)
        else:
            return False
        return True
    except (ValueError, json.JSONDecodeError):
        return False


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
