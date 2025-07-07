"""
Endpoints para gestão de Contratações
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.contratacao import Contratacao
from app.models.usuario import Usuario
from app.schemas.contratacao import (
    ContratacaoResponse,
    ContratacaoCreate,
    ContratacaoUpdate,
    ContratacaoFilter
)
from app.schemas.common import PaginatedResponse
from app.utils.helpers import paginate_query
from app.middleware.rate_limiting import limiter
from app.core.cache import get_cache, set_cache

router = APIRouter(prefix="/contratacoes", tags=["Contratações"])


@router.get("", response_model=PaginatedResponse[ContratacaoResponse])
@limiter.limit("100/minute")
async def listar_contratacoes(
    request,
    filtros: ContratacaoFilter = Depends(),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista contratações com filtros e paginação
    """
    # Verificar cache
    cache_key = f"contratacoes_list_{hash(str(filtros.dict()))}_{page}_{size}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    # Construir query base
    query = db.query(Contratacao)
    
    # Aplicar filtros
    if filtros.ano:
        query = query.filter(
            db.func.extract('year', Contratacao.data_abertura_proposta) == filtros.ano
        )
    
    if filtros.orgao_cnpj:
        query = query.filter(Contratacao.orgao_cnpj == filtros.orgao_cnpj)
    
    if filtros.modalidade:
        query = query.filter(Contratacao.modalidade == filtros.modalidade)
    
    if filtros.situacao:
        query = query.filter(Contratacao.situacao == filtros.situacao)
    
    if filtros.data_inicio:
        query = query.filter(Contratacao.data_abertura_proposta >= filtros.data_inicio)
    
    if filtros.data_fim:
        query = query.filter(Contratacao.data_abertura_proposta <= filtros.data_fim)
    
    if filtros.valor_minimo:
        query = query.filter(Contratacao.valor_total_estimado >= filtros.valor_minimo)
    
    if filtros.valor_maximo:
        query = query.filter(Contratacao.valor_total_estimado <= filtros.valor_maximo)
    
    if filtros.termo_busca:
        query = query.filter(
            or_(
                Contratacao.orgao_nome.ilike(f"%{filtros.termo_busca}%"),
                Contratacao.objeto_contratacao.ilike(f"%{filtros.termo_busca}%"),
                Contratacao.numero_compra.ilike(f"%{filtros.termo_busca}%")
            )
        )
    
    # Aplicar ordenação
    if filtros.ordenar_por == "data_abertura":
        query = query.order_by(Contratacao.data_abertura_proposta.desc())
    elif filtros.ordenar_por == "valor_estimado":
        query = query.order_by(Contratacao.valor_total_estimado.desc())
    else:
        query = query.order_by(Contratacao.created_at.desc())
    
    # Paginar e executar
    result = paginate_query(query, page, size)
    
    # Cache do resultado
    await set_cache(cache_key, result, expire=300)  # 5 minutos
    
    return result


@router.get("/{contratacao_id}", response_model=ContratacaoResponse)
@limiter.limit("200/minute")
async def obter_contratacao(
    request,
    contratacao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém detalhes de uma contratação específica
    """
    # Verificar cache
    cache_key = f"contratacao_{contratacao_id}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    contratacao = db.query(Contratacao).filter(
        Contratacao.id == contratacao_id
    ).first()
    
    if not contratacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contratação não encontrada"
        )
    
    # Cache do resultado
    await set_cache(cache_key, contratacao, expire=600)  # 10 minutos
    
    return contratacao


@router.post("", response_model=ContratacaoResponse)
@limiter.limit("10/minute")
async def criar_contratacao(
    request,
    contratacao_data: ContratacaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cria uma nova contratação
    """
    # Verificar permissões
    if not current_user.is_admin and not current_user.pode_criar_contratacao:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar contratação"
        )
    
    # Verificar se número da compra já existe
    existing_contratacao = db.query(Contratacao).filter(
        and_(
            Contratacao.numero_compra == contratacao_data.numero_compra,
            Contratacao.orgao_cnpj == contratacao_data.orgao_cnpj
        )
    ).first()
    
    if existing_contratacao:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe contratação com este número para o órgão"
        )
    
    # Criar contratação
    contratacao = Contratacao(**contratacao_data.dict())
    contratacao.usuario_id = current_user.id
    
    db.add(contratacao)
    db.commit()
    db.refresh(contratacao)
    
    # Invalidar cache relacionado
    await invalidate_contratacao_cache()
    
    return contratacao


@router.put("/{contratacao_id}", response_model=ContratacaoResponse)
@limiter.limit("10/minute")
async def atualizar_contratacao(
    request,
    contratacao_id: int,
    contratacao_data: ContratacaoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Atualiza uma contratação existente
    """
    contratacao = db.query(Contratacao).filter(
        Contratacao.id == contratacao_id
    ).first()
    
    if not contratacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contratação não encontrada"
        )
    
    # Verificar permissões
    if not current_user.is_admin and contratacao.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar esta contratação"
        )
    
    # Atualizar campos
    update_data = contratacao_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contratacao, field, value)
    
    db.commit()
    db.refresh(contratacao)
    
    # Invalidar cache relacionado
    await invalidate_contratacao_cache(contratacao_id)
    
    return contratacao


@router.delete("/{contratacao_id}")
@limiter.limit("5/minute")
async def deletar_contratacao(
    request,
    contratacao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Deleta uma contratação
    """
    contratacao = db.query(Contratacao).filter(
        Contratacao.id == contratacao_id
    ).first()
    
    if not contratacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contratação não encontrada"
        )
    
    # Verificar permissões
    if not current_user.is_admin and contratacao.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para deletar esta contratação"
        )
    
    # Verificar se há atas ou contratos vinculados
    from app.models.ata import AtaRegistroPreco
    from app.models.contrato import Contrato
    
    atas = db.query(AtaRegistroPreco).filter(AtaRegistroPreco.contratacao_id == contratacao_id).first()
    contratos = db.query(Contrato).filter(
        Contrato.contratacao_id == contratacao_id
    ).first()
    
    if atas or contratos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar contratação com atas ou contratos vinculados"
        )
    
    db.delete(contratacao)
    db.commit()
    
    # Invalidar cache relacionado
    await invalidate_contratacao_cache(contratacao_id)
    
    return {"message": "Contratação deletada com sucesso"}


@router.get("/estatisticas/resumo")
@limiter.limit("30/minute")
async def obter_estatisticas_contratacao(
    request,
    ano: Optional[int] = Query(None, description="Ano para filtrar"),
    orgao_cnpj: Optional[str] = Query(None, description="CNPJ do órgão"),
    modalidade: Optional[str] = Query(None, description="Modalidade"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém estatísticas resumidas das contratações
    """
    cache_key = f"contratacao_stats_{ano}_{orgao_cnpj}_{modalidade}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    # Query base
    query = db.query(Contratacao)
    
    if ano:
        query = query.filter(
            db.func.extract('year', Contratacao.data_abertura_proposta) == ano
        )
    
    if orgao_cnpj:
        query = query.filter(Contratacao.orgao_cnpj == orgao_cnpj)
    
    if modalidade:
        query = query.filter(Contratacao.modalidade == modalidade)
    
    # Calcular estatísticas
    total_contratacoes = query.count()
    valor_total = query.with_entities(
        db.func.sum(Contratacao.valor_total_estimado)
    ).scalar() or 0
    
    # Estatísticas por modalidade
    stats_modalidade = db.query(
        Contratacao.modalidade,
        db.func.count(Contratacao.id).label('quantidade'),
        db.func.sum(Contratacao.valor_total_estimado).label('valor')
    ).group_by(Contratacao.modalidade)
    
    if ano:
        stats_modalidade = stats_modalidade.filter(
            db.func.extract('year', Contratacao.data_abertura_proposta) == ano
        )
    if orgao_cnpj:
        stats_modalidade = stats_modalidade.filter(
            Contratacao.orgao_cnpj == orgao_cnpj
        )
    
    stats_modalidade = stats_modalidade.all()
    
    # Estatísticas por situação
    stats_situacao = db.query(
        Contratacao.situacao,
        db.func.count(Contratacao.id).label('quantidade'),
        db.func.sum(Contratacao.valor_total_estimado).label('valor')
    ).group_by(Contratacao.situacao)
    
    if ano:
        stats_situacao = stats_situacao.filter(
            db.func.extract('year', Contratacao.data_abertura_proposta) == ano
        )
    if orgao_cnpj:
        stats_situacao = stats_situacao.filter(
            Contratacao.orgao_cnpj == orgao_cnpj
        )
    if modalidade:
        stats_situacao = stats_situacao.filter(
            Contratacao.modalidade == modalidade
        )
    
    stats_situacao = stats_situacao.all()
    
    result = {
        "total_contratacoes": total_contratacoes,
        "valor_total": valor_total,
        "por_modalidade": [
            {
                "modalidade": stat.modalidade,
                "quantidade": stat.quantidade,
                "valor": stat.valor or 0
            }
            for stat in stats_modalidade
        ],
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


@router.get("/{contratacao_id}/timeline")
@limiter.limit("50/minute")
async def obter_timeline_contratacao(
    request,
    contratacao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém timeline de eventos da contratação
    """
    contratacao = db.query(Contratacao).filter(
        Contratacao.id == contratacao_id
    ).first()
    
    if not contratacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contratação não encontrada"
        )
    
    # Montar timeline com eventos importantes
    timeline = []
    
    # Evento: Abertura da proposta
    if contratacao.data_abertura_proposta:
        timeline.append({
            "data": contratacao.data_abertura_proposta,
            "evento": "Abertura da proposta",
            "descricao": "Início do processo de contratação"
        })
    
    # Evento: Encerramento da proposta
    if contratacao.data_encerramento_proposta:
        timeline.append({
            "data": contratacao.data_encerramento_proposta,
            "evento": "Encerramento da proposta",
            "descricao": "Fim do prazo para propostas"
        })
    
    # Buscar atas relacionadas
    from app.models.ata import AtaRegistroPreco
    atas = db.query(AtaRegistroPreco).filter(AtaRegistroPreco.contratacao_id == contratacao_id).all()
    
    for ata in atas:
        timeline.append({
            "data": ata.data_publicacao,
            "evento": "Publicação de Ata",
            "descricao": f"Ata #{ata.numero_ata} publicada"
        })
    
    # Buscar contratos relacionados
    from app.models.contrato import Contrato
    contratos = db.query(Contrato).filter(
        Contrato.contratacao_id == contratacao_id
    ).all()
    
    for contrato in contratos:
        timeline.append({
            "data": contrato.data_assinatura,
            "evento": "Assinatura de Contrato",
            "descricao": f"Contrato #{contrato.numero_contrato} assinado"
        })
    
    # Ordenar timeline por data
    timeline.sort(key=lambda x: x["data"])
    
    return {"timeline": timeline}


async def invalidate_contratacao_cache(contratacao_id: Optional[int] = None):
    """
    Invalida cache relacionado às contratações
    """
    from app.core.cache import delete_cache_pattern
    
    # Invalidar cache de listagem
    await delete_cache_pattern("contratacoes_list_*")
    await delete_cache_pattern("contratacao_stats_*")
    
    # Invalidar cache específico se fornecido
    if contratacao_id:
        await delete_cache_pattern(f"contratacao_{contratacao_id}")
