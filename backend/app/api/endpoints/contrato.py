"""
Endpoints para gestão de Contratos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.contrato import Contrato
from app.models.usuario import Usuario
from app.schemas.contrato import (
    ContratoResponse,
    ContratoCreate,
    ContratoUpdate,
    ContratoFilter
)
from app.schemas.common import PaginatedResponse
from app.utils.helpers import paginate_query
from app.middleware.rate_limiting import limiter
from app.core.cache import get_cache, set_cache

router = APIRouter(prefix="/contratos", tags=["Contratos"])


@router.get("", response_model=PaginatedResponse[ContratoResponse])
@limiter.limit("100/minute")
async def listar_contratos(
    request,
    filtros: ContratoFilter = Depends(),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista contratos com filtros e paginação
    """
    # Verificar cache
    cache_key = f"contratos_list_{hash(str(filtros.dict()))}_{page}_{size}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    # Construir query base
    query = db.query(Contrato)
    
    # Aplicar filtros
    if filtros.ano:
        query = query.filter(
            db.func.extract('year', Contrato.data_assinatura) == filtros.ano
        )
    
    if filtros.orgao_cnpj:
        query = query.filter(Contrato.orgao_cnpj == filtros.orgao_cnpj)
    
    if filtros.fornecedor_cnpj:
        query = query.filter(Contrato.fornecedor_cnpj == filtros.fornecedor_cnpj)
    
    if filtros.situacao:
        query = query.filter(Contrato.situacao == filtros.situacao)
    
    if filtros.data_inicio:
        query = query.filter(Contrato.data_assinatura >= filtros.data_inicio)
    
    if filtros.data_fim:
        query = query.filter(Contrato.data_assinatura <= filtros.data_fim)
    
    if filtros.valor_minimo:
        query = query.filter(Contrato.valor_inicial >= filtros.valor_minimo)
    
    if filtros.valor_maximo:
        query = query.filter(Contrato.valor_inicial <= filtros.valor_maximo)
    
    if filtros.vigencia_inicio:
        query = query.filter(Contrato.data_inicio_vigencia >= filtros.vigencia_inicio)
    
    if filtros.vigencia_fim:
        query = query.filter(Contrato.data_fim_vigencia <= filtros.vigencia_fim)
    
    if filtros.termo_busca:
        query = query.filter(
            or_(
                Contrato.orgao_nome.ilike(f"%{filtros.termo_busca}%"),
                Contrato.fornecedor_nome.ilike(f"%{filtros.termo_busca}%"),
                Contrato.numero_contrato.ilike(f"%{filtros.termo_busca}%"),
                Contrato.objeto.ilike(f"%{filtros.termo_busca}%")
            )
        )
    
    # Aplicar ordenação
    if filtros.ordenar_por == "data_assinatura":
        query = query.order_by(Contrato.data_assinatura.desc())
    elif filtros.ordenar_por == "valor_inicial":
        query = query.order_by(Contrato.valor_inicial.desc())
    elif filtros.ordenar_por == "vigencia":
        query = query.order_by(Contrato.data_fim_vigencia.desc())
    else:
        query = query.order_by(Contrato.created_at.desc())
    
    # Paginar e executar
    result = paginate_query(query, page, size)
    
    # Cache do resultado
    await set_cache(cache_key, result, expire=300)  # 5 minutos
    
    return result


@router.get("/{contrato_id}", response_model=ContratoResponse)
@limiter.limit("200/minute")
async def obter_contrato(
    request,
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém detalhes de um contrato específico
    """
    # Verificar cache
    cache_key = f"contrato_{contrato_id}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Cache do resultado
    await set_cache(cache_key, contrato, expire=600)  # 10 minutos
    
    return contrato


@router.post("", response_model=ContratoResponse)
@limiter.limit("10/minute")
async def criar_contrato(
    request,
    contrato_data: ContratoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cria um novo contrato
    """
    # Verificar permissões
    if not current_user.is_admin and not current_user.pode_criar_contrato:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para criar contrato"
        )
    
    # Verificar se número do contrato já existe
    existing_contrato = db.query(Contrato).filter(
        and_(
            Contrato.numero_contrato == contrato_data.numero_contrato,
            Contrato.orgao_cnpj == contrato_data.orgao_cnpj
        )
    ).first()
    
    if existing_contrato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe contrato com este número para o órgão"
        )
    
    # Verificar se a contratação existe
    if contrato_data.contratacao_id:
        from app.models.contratacao import Contratacao
        contratacao = db.query(Contratacao).filter(
            Contratacao.id == contrato_data.contratacao_id
        ).first()
        
        if not contratacao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contratação não encontrada"
            )
    
    # Verificar se a ata existe
    if contrato_data.ata_id:
        from app.models.ata import AtaRegistroPreco
        ata = db.query(AtaRegistroPreco).filter(AtaRegistroPreco.id == contrato_data.ata_id).first()
        
        if not ata:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ata não encontrada"
            )
    
    # Criar contrato
    contrato = Contrato(**contrato_data.dict())
    contrato.usuario_id = current_user.id
    
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    
    # Invalidar cache relacionado
    await invalidate_contrato_cache()
    
    return contrato


@router.put("/{contrato_id}", response_model=ContratoResponse)
@limiter.limit("10/minute")
async def atualizar_contrato(
    request,
    contrato_id: int,
    contrato_data: ContratoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Atualiza um contrato existente
    """
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Verificar permissões
    if not current_user.is_admin and contrato.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar este contrato"
        )
    
    # Atualizar campos
    update_data = contrato_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contrato, field, value)
    
    db.commit()
    db.refresh(contrato)
    
    # Invalidar cache relacionado
    await invalidate_contrato_cache(contrato_id)
    
    return contrato


@router.delete("/{contrato_id}")
@limiter.limit("5/minute")
async def deletar_contrato(
    request,
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Deleta um contrato
    """
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Verificar permissões
    if not current_user.is_admin and contrato.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para deletar este contrato"
        )
    
    # Verificar se o contrato pode ser deletado
    if contrato.situacao in ["ATIVO", "SUSPENSO"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar contrato ativo ou suspenso"
        )
    
    db.delete(contrato)
    db.commit()
    
    # Invalidar cache relacionado
    await invalidate_contrato_cache(contrato_id)
    
    return {"message": "Contrato deletado com sucesso"}


@router.get("/estatisticas/resumo")
@limiter.limit("30/minute")
async def obter_estatisticas_contrato(
    request,
    ano: Optional[int] = Query(None, description="Ano para filtrar"),
    orgao_cnpj: Optional[str] = Query(None, description="CNPJ do órgão"),
    fornecedor_cnpj: Optional[str] = Query(None, description="CNPJ do fornecedor"),
    situacao: Optional[str] = Query(None, description="Situação do contrato"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém estatísticas resumidas dos contratos
    """
    cache_key = f"contrato_stats_{ano}_{orgao_cnpj}_{fornecedor_cnpj}_{situacao}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    # Query base
    query = db.query(Contrato)
    
    if ano:
        query = query.filter(
            db.func.extract('year', Contrato.data_assinatura) == ano
        )
    
    if orgao_cnpj:
        query = query.filter(Contrato.orgao_cnpj == orgao_cnpj)
    
    if fornecedor_cnpj:
        query = query.filter(Contrato.fornecedor_cnpj == fornecedor_cnpj)
    
    if situacao:
        query = query.filter(Contrato.situacao == situacao)
    
    # Calcular estatísticas
    total_contratos = query.count()
    valor_total = query.with_entities(
        db.func.sum(Contrato.valor_inicial)
    ).scalar() or 0
    
    # Contratos ativos
    import datetime
    contratos_ativos = query.filter(
        and_(
            Contrato.situacao == "ATIVO",
            Contrato.data_inicio_vigencia <= datetime.date.today(),
            Contrato.data_fim_vigencia >= datetime.date.today()
        )
    ).count()
    
    # Contratos vencidos
    contratos_vencidos = query.filter(
        or_(
            Contrato.situacao == "ENCERRADO",
            Contrato.data_fim_vigencia < datetime.date.today()
        )
    ).count()
    
    # Estatísticas por situação
    stats_situacao = db.query(
        Contrato.situacao,
        db.func.count(Contrato.id).label('quantidade'),
        db.func.sum(Contrato.valor_inicial).label('valor')
    ).group_by(Contrato.situacao)
    
    if ano:
        stats_situacao = stats_situacao.filter(
            db.func.extract('year', Contrato.data_assinatura) == ano
        )
    if orgao_cnpj:
        stats_situacao = stats_situacao.filter(
            Contrato.orgao_cnpj == orgao_cnpj
        )
    if fornecedor_cnpj:
        stats_situacao = stats_situacao.filter(
            Contrato.fornecedor_cnpj == fornecedor_cnpj
        )
    
    stats_situacao = stats_situacao.all()
    
    # Top fornecedores
    top_fornecedores = db.query(
        Contrato.fornecedor_nome,
        Contrato.fornecedor_cnpj,
        db.func.count(Contrato.id).label('quantidade'),
        db.func.sum(Contrato.valor_inicial).label('valor')
    ).group_by(
        Contrato.fornecedor_nome,
        Contrato.fornecedor_cnpj
    ).order_by(
        db.func.sum(Contrato.valor_inicial).desc()
    ).limit(10)
    
    if ano:
        top_fornecedores = top_fornecedores.filter(
            db.func.extract('year', Contrato.data_assinatura) == ano
        )
    if orgao_cnpj:
        top_fornecedores = top_fornecedores.filter(
            Contrato.orgao_cnpj == orgao_cnpj
        )
    
    top_fornecedores = top_fornecedores.all()
    
    result = {
        "total_contratos": total_contratos,
        "valor_total": valor_total,
        "contratos_ativos": contratos_ativos,
        "contratos_vencidos": contratos_vencidos,
        "por_situacao": [
            {
                "situacao": stat.situacao,
                "quantidade": stat.quantidade,
                "valor": stat.valor or 0
            }
            for stat in stats_situacao
        ],
        "top_fornecedores": [
            {
                "nome": fornecedor.fornecedor_nome,
                "cnpj": fornecedor.fornecedor_cnpj,
                "quantidade": fornecedor.quantidade,
                "valor": fornecedor.valor or 0
            }
            for fornecedor in top_fornecedores
        ]
    }
    
    # Cache do resultado
    await set_cache(cache_key, result, expire=900)  # 15 minutos
    
    return result


@router.get("/{contrato_id}/vigencia")
@limiter.limit("50/minute")
async def verificar_vigencia_contrato(
    request,
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Verifica a vigência de um contrato
    """
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    import datetime
    hoje = datetime.date.today()
    
    # Verificar situação da vigência
    if contrato.data_inicio_vigencia > hoje:
        status_vigencia = "nao_iniciado"
        dias_para_inicio = (contrato.data_inicio_vigencia - hoje).days
        dias_para_fim = None
    elif contrato.data_fim_vigencia < hoje:
        status_vigencia = "vencido"
        dias_para_inicio = None
        dias_para_fim = (hoje - contrato.data_fim_vigencia).days
    else:
        status_vigencia = "vigente"
        dias_para_inicio = None
        dias_para_fim = (contrato.data_fim_vigencia - hoje).days
    
    # Verificar se pode ser prorrogado
    pode_prorrogar = (
        contrato.situacao == "ATIVO" and
        status_vigencia == "vigente" and
        dias_para_fim is not None and
        dias_para_fim <= 90  # 3 meses antes do vencimento
    )
    
    return {
        "contrato_id": contrato_id,
        "numero_contrato": contrato.numero_contrato,
        "data_inicio_vigencia": contrato.data_inicio_vigencia,
        "data_fim_vigencia": contrato.data_fim_vigencia,
        "status_vigencia": status_vigencia,
        "situacao_contrato": contrato.situacao,
        "dias_para_inicio": dias_para_inicio,
        "dias_para_fim": dias_para_fim,
        "alerta_vencimento": dias_para_fim is not None and dias_para_fim <= 30,
        "pode_prorrogar": pode_prorrogar
    }


@router.post("/{contrato_id}/prorrogar")
@limiter.limit("10/minute")
async def prorrogar_contrato(
    request,
    contrato_id: int,
    nova_data_fim: str = Query(..., description="Nova data de fim (YYYY-MM-DD)"),
    justificativa: str = Query(..., description="Justificativa para prorrogação"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Prorroga a vigência de um contrato
    """
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Verificar permissões
    if not current_user.is_admin and not current_user.pode_prorrogar_contrato:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para prorrogar contrato"
        )
    
    # Verificar se contrato pode ser prorrogado
    if contrato.situacao != "ATIVO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas contratos ativos podem ser prorrogados"
        )
    
    # Validar nova data
    import datetime
    try:
        nova_data = datetime.datetime.strptime(nova_data_fim, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data inválida. Use o formato YYYY-MM-DD"
        )
    
    if nova_data <= contrato.data_fim_vigencia:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova data deve ser posterior à data atual de fim"
        )
    
    # Atualizar contrato
    data_fim_anterior = contrato.data_fim_vigencia
    contrato.data_fim_vigencia = nova_data
    contrato.prorrogado = True
    contrato.justificativa_prorrogacao = justificativa
    
    db.commit()
    db.refresh(contrato)
    
    # Invalidar cache relacionado
    await invalidate_contrato_cache(contrato_id)
    
    return {
        "message": "Contrato prorrogado com sucesso",
        "contrato_id": contrato_id,
        "data_fim_anterior": data_fim_anterior,
        "nova_data_fim": nova_data,
        "justificativa": justificativa
    }


@router.get("/{contrato_id}/historico")
@limiter.limit("50/minute")
async def obter_historico_contrato(
    request,
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtém histórico de alterações do contrato
    """
    contrato = db.query(Contrato).filter(Contrato.id == contrato_id).first()
    
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado"
        )
    
    # Montar histórico com eventos importantes
    historico = []
    
    # Evento: Assinatura
    historico.append({
        "data": contrato.data_assinatura,
        "evento": "Assinatura do contrato",
        "descricao": f"Contrato {contrato.numero_contrato} assinado",
        "valor": contrato.valor_inicial
    })
    
    # Evento: Início da vigência
    historico.append({
        "data": contrato.data_inicio_vigencia,
        "evento": "Início da vigência",
        "descricao": "Contrato entrou em vigor",
        "valor": None
    })
    
    # Evento: Prorrogação (se houver)
    if contrato.prorrogado:
        historico.append({
            "data": contrato.updated_at.date(),
            "evento": "Prorrogação",
            "descricao": contrato.justificativa_prorrogacao or "Contrato prorrogado",
            "valor": None
        })
    
    # Evento: Fim da vigência
    historico.append({
        "data": contrato.data_fim_vigencia,
        "evento": "Fim da vigência",
        "descricao": "Fim previsto da vigência do contrato",
        "valor": None
    })
    
    # Ordenar histórico por data
    historico.sort(key=lambda x: x["data"])
    
    return {
        "contrato_id": contrato_id,
        "numero_contrato": contrato.numero_contrato,
        "historico": historico
    }


async def invalidate_contrato_cache(contrato_id: Optional[int] = None):
    """
    Invalida cache relacionado aos contratos
    """
    from app.core.cache import delete_cache_pattern
    
    # Invalidar cache de listagem
    await delete_cache_pattern("contratos_list_*")
    await delete_cache_pattern("contrato_stats_*")
    
    # Invalidar cache específico se fornecido
    if contrato_id:
        await delete_cache_pattern(f"contrato_{contrato_id}")
