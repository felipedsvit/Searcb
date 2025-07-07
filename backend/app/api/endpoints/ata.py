"""
Endpoints para gestão de Atas de Registro de Preços
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.ata import Ata
from app.models.contrato import Usuario
from app.schemas.ata import (
    AtaResponse,
    AtaCreate,
    AtaUpdate,
    AtaFilter
)
from app.schemas.common import PaginatedResponse
from app.utils.helpers import paginate_query
from app.middleware.rate_limiting import limiter
from app.core.cache import get_cache, set_cache

router = APIRouter(prefix="/atas", tags=["Atas"])


@router.get("", response_model=PaginatedResponse[AtaResponse])
@limiter.limit("100/minute")
async def listar_atas(
    request,
    filtros: AtaFilter = Depends(),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista atas com filtros e paginação
    """
    # Verificar cache
    cache_key = f"atas_list_{hash(str(filtros.dict()))}_{page}_{size}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    # Construir query base
    query = db.query(Ata)
    
    # Aplicar filtros
    if filtros.ano:
        query = query.filter(
            db.func.extract('year', Ata.data_publicacao) == filtros.ano
        )
    
    if filtros.orgao_cnpj:
        query = query.filter(Ata.orgao_cnpj == filtros.orgao_cnpj)
    
    if filtros.situacao:
        query = query.filter(Ata.situacao == filtros.situacao)
    
    if filtros.data_inicio:
        query = query.filter(Ata.data_publicacao >= filtros.data_inicio)
    
    if filtros.data_fim:
        query = query.filter(Ata.data_publicacao <= filtros.data_fim)
    
    if filtros.valor_minimo:
        query = query.filter(Ata.valor_total >= filtros.valor_minimo)
    
    if filtros.valor_maximo:
        query = query.filter(Ata.valor_total <= filtros.valor_maximo)
    
    if filtros.vigencia_inicio:
        query = query.filter(Ata.data_inicio_vigencia >= filtros.vigencia_inicio)
    
    if filtros.vigencia_fim:
        query = query.filter(Ata.data_fim_vigencia <= filtros.vigencia_fim)
    
    if filtros.termo_busca:
        query = query.filter(
            or_(
                Ata.orgao_nome.ilike(f"%{filtros.termo_busca}%"),
                Ata.numero_ata.ilike(f"%{filtros.termo_busca}%"),
                Ata.objeto.ilike(f"%{filtros.termo_busca}%")
            )
        )
    
    # Aplicar ordenação
    if filtros.ordenar_por == "data_publicacao":
        query = query.order_by(Ata.data_publicacao.desc())
    elif filtros.ordenar_por == "valor_total":
        query = query.order_by(Ata.valor_total.desc())
    elif filtros.ordenar_por == "vigencia":
        query = query.order_by(Ata.data_fim_vigencia.desc())
    else:
        query = query.order_by(Ata.created_at.desc())
    
    # Paginar e executar
    result = paginate_query(query, page, size)
    
    # Cache do resultado
    await set_cache(cache_key, result, expire=300)  # 5 minutos
    
    return result


@router.get("/{ata_id}", response_model=AtaResponse)
@limiter.limit("200/minute")
async def obter_ata(
    request,
    ata_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém detalhes de uma ata específica
    """
    # Verificar cache
    cache_key = f"ata_{ata_id}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    ata = db.query(Ata).filter(Ata.id == ata_id).first()
    
    if not ata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ata não encontrada"
        )
    
    # Cache do resultado
    await set_cache(cache_key, ata, expire=600)  # 10 minutos
    
    return ata


@router.post("", response_model=AtaResponse)
@limiter.limit("10/minute")
async def criar_ata(
    request,
    ata_data: AtaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cria uma nova ata
    """
    # Verificar permissões
    if not current_user.is_admin and not current_user.pode_criar_ata:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar ata"
        )
    
    # Verificar se número da ata já existe
    existing_ata = db.query(Ata).filter(
        and_(
            Ata.numero_ata == ata_data.numero_ata,
            Ata.orgao_cnpj == ata_data.orgao_cnpj
        )
    ).first()
    
    if existing_ata:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe ata com este número para o órgão"
        )
    
    # Verificar se a contratação existe
    if ata_data.contratacao_id:
        from app.models.contratacao import Contratacao
        contratacao = db.query(Contratacao).filter(
            Contratacao.id == ata_data.contratacao_id
        ).first()
        
        if not contratacao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contratação não encontrada"
            )
    
    # Criar ata
    ata = Ata(**ata_data.dict())
    ata.usuario_id = current_user.id
    
    db.add(ata)
    db.commit()
    db.refresh(ata)
    
    # Invalidar cache relacionado
    await invalidate_ata_cache()
    
    return ata


@router.put("/{ata_id}", response_model=AtaResponse)
@limiter.limit("10/minute")
async def atualizar_ata(
    request,
    ata_id: int,
    ata_data: AtaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Atualiza uma ata existente
    """
    ata = db.query(Ata).filter(Ata.id == ata_id).first()
    
    if not ata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ata não encontrada"
        )
    
    # Verificar permissões
    if not current_user.is_admin and ata.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar esta ata"
        )
    
    # Atualizar campos
    update_data = ata_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ata, field, value)
    
    db.commit()
    db.refresh(ata)
    
    # Invalidar cache relacionado
    await invalidate_ata_cache(ata_id)
    
    return ata


@router.delete("/{ata_id}")
@limiter.limit("5/minute")
async def deletar_ata(
    request,
    ata_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Deleta uma ata
    """
    ata = db.query(Ata).filter(Ata.id == ata_id).first()
    
    if not ata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ata não encontrada"
        )
    
    # Verificar permissões
    if not current_user.is_admin and ata.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para deletar esta ata"
        )
    
    # Verificar se há contratos vinculados
    from app.models.contrato import Contrato
    contratos = db.query(Contrato).filter(Contrato.ata_id == ata_id).first()
    
    if contratos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar ata com contratos vinculados"
        )
    
    db.delete(ata)
    db.commit()
    
    # Invalidar cache relacionado
    await invalidate_ata_cache(ata_id)
    
    return {"message": "Ata deletada com sucesso"}


@router.get("/estatisticas/resumo")
@limiter.limit("30/minute")
async def obter_estatisticas_ata(
    request,
    ano: Optional[int] = Query(None, description="Ano para filtrar"),
    orgao_cnpj: Optional[str] = Query(None, description="CNPJ do órgão"),
    situacao: Optional[str] = Query(None, description="Situação da ata"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém estatísticas resumidas das atas
    """
    cache_key = f"ata_stats_{ano}_{orgao_cnpj}_{situacao}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    # Query base
    query = db.query(Ata)
    
    if ano:
        query = query.filter(
            db.func.extract('year', Ata.data_publicacao) == ano
        )
    
    if orgao_cnpj:
        query = query.filter(Ata.orgao_cnpj == orgao_cnpj)
    
    if situacao:
        query = query.filter(Ata.situacao == situacao)
    
    # Calcular estatísticas
    total_atas = query.count()
    valor_total = query.with_entities(
        db.func.sum(Ata.valor_total)
    ).scalar() or 0
    
    # Atas vigentes
    import datetime
    atas_vigentes = query.filter(
        and_(
            Ata.data_inicio_vigencia <= datetime.date.today(),
            Ata.data_fim_vigencia >= datetime.date.today()
        )
    ).count()
    
    # Atas vencidas
    atas_vencidas = query.filter(
        Ata.data_fim_vigencia < datetime.date.today()
    ).count()
    
    # Estatísticas por situação
    stats_situacao = db.query(
        Ata.situacao,
        db.func.count(Ata.id).label('quantidade'),
        db.func.sum(Ata.valor_total).label('valor')
    ).group_by(Ata.situacao)
    
    if ano:
        stats_situacao = stats_situacao.filter(
            db.func.extract('year', Ata.data_publicacao) == ano
        )
    if orgao_cnpj:
        stats_situacao = stats_situacao.filter(Ata.orgao_cnpj == orgao_cnpj)
    
    stats_situacao = stats_situacao.all()
    
    result = {
        "total_atas": total_atas,
        "valor_total": valor_total,
        "atas_vigentes": atas_vigentes,
        "atas_vencidas": atas_vencidas,
        "por_situacao": [
            {
                "situacao": stat.situacao,
                "quantidade": stat.quantidade,
                "valor": stat.valor or 0
            }
            for stat in stats_situacao
        ]
    }
    
    # Cache do resultado
    await set_cache(cache_key, result, expire=900)  # 15 minutos
    
    return result


@router.get("/{ata_id}/fornecedores")
@limiter.limit("50/minute")
async def obter_fornecedores_ata(
    request,
    ata_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém lista de fornecedores da ata
    """
    ata = db.query(Ata).filter(Ata.id == ata_id).first()
    
    if not ata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ata não encontrada"
        )
    
    # Buscar fornecedores através dos contratos
    from app.models.contrato import Contrato
    contratos = db.query(Contrato).filter(Contrato.ata_id == ata_id).all()
    
    fornecedores = []
    for contrato in contratos:
        fornecedor = {
            "contrato_id": contrato.id,
            "numero_contrato": contrato.numero_contrato,
            "fornecedor_nome": contrato.fornecedor_nome,
            "fornecedor_cnpj": contrato.fornecedor_cnpj,
            "valor_contrato": contrato.valor_inicial,
            "situacao": contrato.situacao,
            "data_assinatura": contrato.data_assinatura
        }
        fornecedores.append(fornecedor)
    
    return {
        "ata_id": ata_id,
        "numero_ata": ata.numero_ata,
        "fornecedores": fornecedores
    }


@router.get("/{ata_id}/vigencia")
@limiter.limit("50/minute")
async def verificar_vigencia_ata(
    request,
    ata_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Verifica a vigência de uma ata
    """
    ata = db.query(Ata).filter(Ata.id == ata_id).first()
    
    if not ata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ata não encontrada"
        )
    
    import datetime
    hoje = datetime.date.today()
    
    # Verificar situação da vigência
    if ata.data_inicio_vigencia > hoje:
        status_vigencia = "nao_iniciada"
        dias_para_inicio = (ata.data_inicio_vigencia - hoje).days
        dias_para_fim = None
    elif ata.data_fim_vigencia < hoje:
        status_vigencia = "vencida"
        dias_para_inicio = None
        dias_para_fim = (hoje - ata.data_fim_vigencia).days
    else:
        status_vigencia = "vigente"
        dias_para_inicio = None
        dias_para_fim = (ata.data_fim_vigencia - hoje).days
    
    return {
        "ata_id": ata_id,
        "numero_ata": ata.numero_ata,
        "data_inicio_vigencia": ata.data_inicio_vigencia,
        "data_fim_vigencia": ata.data_fim_vigencia,
        "status_vigencia": status_vigencia,
        "dias_para_inicio": dias_para_inicio,
        "dias_para_fim": dias_para_fim,
        "alerta_vencimento": dias_para_fim is not None and dias_para_fim <= 30
    }


async def invalidate_ata_cache(ata_id: Optional[int] = None):
    """
    Invalida cache relacionado às atas
    """
    from app.core.cache import delete_cache_pattern
    
    # Invalidar cache de listagem
    await delete_cache_pattern("atas_list_*")
    await delete_cache_pattern("ata_stats_*")
    
    # Invalidar cache específico se fornecido
    if ata_id:
        await delete_cache_pattern(f"ata_{ata_id}")
