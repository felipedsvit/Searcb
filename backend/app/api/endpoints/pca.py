"""
Endpoints para gestão de PCAs (Planos de Contratações Anuais)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.pca import PCA
from app.models.contrato import Usuario
from app.schemas.pca import (
    PCAResponse,
    PCACreate,
    PCAUpdate,
    PCAFilter,
    PCAList
)
from app.schemas.common import PaginatedResponse
from app.utils.helpers import paginate_query
from app.middleware.rate_limiting import limiter
from app.core.cache import get_cache, set_cache

router = APIRouter(prefix="/pca", tags=["PCA"])


@router.get("", response_model=PaginatedResponse[PCAResponse])
@limiter.limit("100/minute")
async def listar_pcas(
    request,
    filtros: PCAFilter = Depends(),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista PCAs com filtros e paginação
    """
    # Verificar cache
    cache_key = f"pca_list_{hash(str(filtros.dict()))}_{page}_{size}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    # Construir query base
    query = db.query(PCA)
    
    # Aplicar filtros
    if filtros.ano:
        query = query.filter(PCA.ano == filtros.ano)
    
    if filtros.orgao_cnpj:
        query = query.filter(PCA.orgao_cnpj == filtros.orgao_cnpj)
    
    if filtros.status:
        query = query.filter(PCA.status == filtros.status)
    
    if filtros.data_inicio:
        query = query.filter(PCA.data_publicacao >= filtros.data_inicio)
    
    if filtros.data_fim:
        query = query.filter(PCA.data_publicacao <= filtros.data_fim)
    
    if filtros.valor_minimo:
        query = query.filter(PCA.valor_total >= filtros.valor_minimo)
    
    if filtros.valor_maximo:
        query = query.filter(PCA.valor_total <= filtros.valor_maximo)
    
    if filtros.termo_busca:
        query = query.filter(
            or_(
                PCA.orgao_nome.ilike(f"%{filtros.termo_busca}%"),
                PCA.titulo.ilike(f"%{filtros.termo_busca}%"),
                PCA.descricao.ilike(f"%{filtros.termo_busca}%")
            )
        )
    
    # Aplicar ordenação
    if filtros.ordenar_por == "data_publicacao":
        query = query.order_by(PCA.data_publicacao.desc())
    elif filtros.ordenar_por == "valor_total":
        query = query.order_by(PCA.valor_total.desc())
    else:
        query = query.order_by(PCA.created_at.desc())
    
    # Paginar e executar
    result = paginate_query(query, page, size)
    
    # Cache do resultado
    await set_cache(cache_key, result, expire=300)  # 5 minutos
    
    return result


@router.get("/{pca_id}", response_model=PCAResponse)
@limiter.limit("200/minute")
async def obter_pca(
    request,
    pca_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém detalhes de um PCA específico
    """
    # Verificar cache
    cache_key = f"pca_{pca_id}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    pca = db.query(PCA).filter(PCA.id == pca_id).first()
    if not pca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PCA não encontrado"
        )
    
    # Cache do resultado
    await set_cache(cache_key, pca, expire=600)  # 10 minutos
    
    return pca


@router.post("", response_model=PCAResponse)
@limiter.limit("10/minute")
async def criar_pca(
    request,
    pca_data: PCACreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cria um novo PCA
    """
    # Verificar permissões
    if not current_user.is_admin and not current_user.pode_criar_pca:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar PCA"
        )
    
    # Verificar se já existe PCA para o mesmo órgão e ano
    existing_pca = db.query(PCA).filter(
        and_(
            PCA.orgao_cnpj == pca_data.orgao_cnpj,
            PCA.ano == pca_data.ano
        )
    ).first()
    
    if existing_pca:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe PCA para este órgão e ano"
        )
    
    # Criar PCA
    pca = PCA(**pca_data.dict())
    pca.usuario_id = current_user.id
    
    db.add(pca)
    db.commit()
    db.refresh(pca)
    
    # Invalidar cache relacionado
    await invalidate_pca_cache()
    
    return pca


@router.put("/{pca_id}", response_model=PCAResponse)
@limiter.limit("10/minute")
async def atualizar_pca(
    request,
    pca_id: int,
    pca_data: PCAUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Atualiza um PCA existente
    """
    pca = db.query(PCA).filter(PCA.id == pca_id).first()
    if not pca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PCA não encontrado"
        )
    
    # Verificar permissões
    if not current_user.is_admin and pca.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar este PCA"
        )
    
    # Atualizar campos
    update_data = pca_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pca, field, value)
    
    db.commit()
    db.refresh(pca)
    
    # Invalidar cache relacionado
    await invalidate_pca_cache(pca_id)
    
    return pca


@router.delete("/{pca_id}")
@limiter.limit("5/minute")
async def deletar_pca(
    request,
    pca_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Deleta um PCA
    """
    pca = db.query(PCA).filter(PCA.id == pca_id).first()
    if not pca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PCA não encontrado"
        )
    
    # Verificar permissões
    if not current_user.is_admin and pca.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para deletar este PCA"
        )
    
    # Verificar se há contratações vinculadas
    from app.models.contratacao import Contratacao
    contratacoes = db.query(Contratacao).filter(
        Contratacao.pca_id == pca_id
    ).first()
    
    if contratacoes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar PCA com contratações vinculadas"
        )
    
    db.delete(pca)
    db.commit()
    
    # Invalidar cache relacionado
    await invalidate_pca_cache(pca_id)
    
    return {"message": "PCA deletado com sucesso"}


@router.get("/estatisticas/resumo")
@limiter.limit("30/minute")
async def obter_estatisticas_pca(
    request,
    ano: Optional[int] = Query(None, description="Ano para filtrar"),
    orgao_cnpj: Optional[str] = Query(None, description="CNPJ do órgão"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém estatísticas resumidas dos PCAs
    """
    cache_key = f"pca_stats_{ano}_{orgao_cnpj}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    # Query base
    query = db.query(PCA)
    
    if ano:
        query = query.filter(PCA.ano == ano)
    
    if orgao_cnpj:
        query = query.filter(PCA.orgao_cnpj == orgao_cnpj)
    
    # Calcular estatísticas
    total_pcas = query.count()
    valor_total = query.with_entities(
        db.func.sum(PCA.valor_total)
    ).scalar() or 0
    
    # Estatísticas por status
    stats_status = db.query(
        PCA.status,
        db.func.count(PCA.id).label('quantidade'),
        db.func.sum(PCA.valor_total).label('valor')
    ).group_by(PCA.status)
    
    if ano:
        stats_status = stats_status.filter(PCA.ano == ano)
    if orgao_cnpj:
        stats_status = stats_status.filter(PCA.orgao_cnpj == orgao_cnpj)
    
    stats_status = stats_status.all()
    
    result = {
        "total_pcas": total_pcas,
        "valor_total": valor_total,
        "por_status": [
            {
                "status": stat.status,
                "quantidade": stat.quantidade,
                "valor": stat.valor or 0
            }
            for stat in stats_status
        ]
    }
    
    # Cache do resultado
    await set_cache(cache_key, result, expire=900)  # 15 minutos
    
    return result


async def invalidate_pca_cache(pca_id: Optional[int] = None):
    """
    Invalida cache relacionado aos PCAs
    """
    from app.core.cache import delete_cache_pattern
    
    # Invalidar cache de listagem
    await delete_cache_pattern("pca_list_*")
    await delete_cache_pattern("pca_stats_*")
    
    # Invalidar cache específico se fornecido
    if pca_id:
        await delete_cache_pattern(f"pca_{pca_id}")
