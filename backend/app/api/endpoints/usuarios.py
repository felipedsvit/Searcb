"""
Endpoints para gestão de usuários
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.services.usuario_service import (
    UsuarioService, PerfilUsuarioService, LogSistemaService, ConfiguracaoSistemaService
)
from app.schemas.usuario import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse, PerfilUsuarioCreate,
    PerfilUsuarioUpdate, PerfilUsuarioResponse, LogSistemaResponse,
    ConfiguracaoSistemaCreate, ConfiguracaoSistemaUpdate, ConfiguracaoSistemaResponse,
    ChangePasswordRequest, PaginatedUsuarioResponse, PaginatedPerfilUsuarioResponse,
    PaginatedLogSistemaResponse, PaginatedConfiguracaoSistemaResponse
)
from app.schemas.common import ErrorResponse
from app.models.usuario import Usuario
from app.middleware.rate_limiting import rate_limit

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedUsuarioResponse,
    summary="Listar usuários",
    description="Lista usuários com filtros e paginação",
    responses={
        200: {"description": "Lista de usuários retornada com sucesso"},
        403: {"model": ErrorResponse, "description": "Sem permissão para acessar usuários"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
@rate_limit(max_requests=100, window_seconds=3600)
async def list_usuarios(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    search: Optional[str] = Query(None, description="Busca por username, email ou nome"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    is_admin: Optional[bool] = Query(None, description="Filtrar por administradores"),
    orgao_cnpj: Optional[str] = Query(None, description="Filtrar por CNPJ do órgão"),
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Lista usuários com filtros e paginação.
    
    **Parâmetros:**
    - **page**: Número da página (padrão: 1)
    - **size**: Tamanho da página (padrão: 20, máximo: 100)
    - **search**: Busca por username, email ou nome
    - **ativo**: Filtrar por status ativo
    - **is_admin**: Filtrar por administradores
    - **orgao_cnpj**: Filtrar por CNPJ do órgão
    
    **Retorna:**
    - Lista paginada de usuários
    """
    usuario_service = UsuarioService(db)
    
    skip = (page - 1) * size
    
    # Buscar usuários
    usuarios = await usuario_service.list_usuarios(
        skip=skip,
        limit=size,
        search=search,
        ativo=ativo,
        is_admin=is_admin,
        orgao_cnpj=orgao_cnpj
    )
    
    # Contar total
    total = await usuario_service.count_usuarios(
        search=search,
        ativo=ativo,
        is_admin=is_admin,
        orgao_cnpj=orgao_cnpj
    )
    
    return PaginatedUsuarioResponse(
        items=usuarios,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Obter usuário por ID",
    description="Obtém detalhes de um usuário específico",
    responses={
        200: {"description": "Usuário retornado com sucesso"},
        404: {"model": ErrorResponse, "description": "Usuário não encontrado"},
        403: {"model": ErrorResponse, "description": "Sem permissão para acessar usuário"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
@rate_limit(max_requests=200, window_seconds=3600)
async def get_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes de um usuário específico.
    
    **Parâmetros:**
    - **usuario_id**: ID do usuário
    
    **Retorna:**
    - Dados do usuário
    """
    usuario_service = UsuarioService(db)
    
    # Verificar se o usuário pode acessar este recurso
    if not current_user.is_admin and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este usuário"
        )
    
    usuario = await usuario_service.get_usuario_by_id(usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return usuario


@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar usuário",
    description="Cria um novo usuário no sistema",
    responses={
        201: {"description": "Usuário criado com sucesso"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        403: {"model": ErrorResponse, "description": "Sem permissão para criar usuário"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
@rate_limit(max_requests=10, window_seconds=3600)
async def create_usuario(
    usuario_data: UsuarioCreate,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo usuário no sistema.
    
    **Parâmetros:**
    - **usuario_data**: Dados do usuário a ser criado
    
    **Retorna:**
    - Dados do usuário criado
    """
    usuario_service = UsuarioService(db)
    
    usuario = await usuario_service.create_usuario(usuario_data)
    
    return usuario


@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Atualizar usuário",
    description="Atualiza dados de um usuário existente",
    responses={
        200: {"description": "Usuário atualizado com sucesso"},
        404: {"model": ErrorResponse, "description": "Usuário não encontrado"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        403: {"model": ErrorResponse, "description": "Sem permissão para atualizar usuário"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
@rate_limit(max_requests=20, window_seconds=3600)
async def update_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza dados de um usuário existente.
    
    **Parâmetros:**
    - **usuario_id**: ID do usuário
    - **usuario_data**: Dados para atualização
    
    **Retorna:**
    - Dados do usuário atualizado
    """
    usuario_service = UsuarioService(db)
    
    # Verificar se o usuário pode atualizar este recurso
    if not current_user.is_admin and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar este usuário"
        )
    
    # Usuários não-admin não podem alterar permissões
    if not current_user.is_admin:
        usuario_data.is_admin = None
        usuario_data.is_gestor = None
        usuario_data.ativo = None
    
    usuario = await usuario_service.update_usuario(usuario_id, usuario_data)
    
    return usuario


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover usuário",
    description="Remove um usuário do sistema (soft delete)",
    responses={
        204: {"description": "Usuário removido com sucesso"},
        404: {"model": ErrorResponse, "description": "Usuário não encontrado"},
        403: {"model": ErrorResponse, "description": "Sem permissão para remover usuário"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
@rate_limit(max_requests=5, window_seconds=3600)
async def delete_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Remove um usuário do sistema (soft delete).
    
    **Parâmetros:**
    - **usuario_id**: ID do usuário
    """
    usuario_service = UsuarioService(db)
    
    await usuario_service.delete_usuario(usuario_id)


@router.post(
    "/{usuario_id}/change-password",
    status_code=status.HTTP_200_OK,
    summary="Alterar senha",
    description="Altera a senha de um usuário",
    responses={
        200: {"description": "Senha alterada com sucesso"},
        404: {"model": ErrorResponse, "description": "Usuário não encontrado"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        403: {"model": ErrorResponse, "description": "Sem permissão para alterar senha"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
@rate_limit(max_requests=5, window_seconds=3600)
async def change_password(
    usuario_id: int,
    password_data: ChangePasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Altera a senha de um usuário.
    
    **Parâmetros:**
    - **usuario_id**: ID do usuário
    - **password_data**: Dados da mudança de senha
    
    **Retorna:**
    - Mensagem de confirmação
    """
    usuario_service = UsuarioService(db)
    
    # Verificar se o usuário pode alterar a senha
    if not current_user.is_admin and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para alterar senha deste usuário"
        )
    
    await usuario_service.change_password(usuario_id, password_data)
    
    return {"message": "Senha alterada com sucesso"}


# Rotas para perfis
@router.get(
    "/perfis",
    response_model=PaginatedPerfilUsuarioResponse,
    summary="Listar perfis",
    description="Lista perfis de usuário com filtros e paginação",
    responses={
        200: {"description": "Lista de perfis retornada com sucesso"},
        403: {"model": ErrorResponse, "description": "Sem permissão para acessar perfis"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
@rate_limit(max_requests=100, window_seconds=3600)
async def list_perfis(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    search: Optional[str] = Query(None, description="Busca por nome ou descrição"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Lista perfis de usuário com filtros e paginação.
    """
    perfil_service = PerfilUsuarioService(db)
    
    skip = (page - 1) * size
    
    perfis = await perfil_service.list_perfis(
        skip=skip,
        limit=size,
        search=search,
        ativo=ativo
    )
    
    total = len(perfis)  # TODO: Implementar count
    
    return PaginatedPerfilUsuarioResponse(
        items=perfis,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post(
    "/perfis",
    response_model=PerfilUsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar perfil",
    description="Cria um novo perfil de usuário",
    responses={
        201: {"description": "Perfil criado com sucesso"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        403: {"model": ErrorResponse, "description": "Sem permissão para criar perfil"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
@rate_limit(max_requests=10, window_seconds=3600)
async def create_perfil(
    perfil_data: PerfilUsuarioCreate,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo perfil de usuário.
    """
    perfil_service = PerfilUsuarioService(db)
    
    perfil = await perfil_service.create_perfil(perfil_data)
    
    return perfil


# Rotas para logs
@router.get(
    "/logs",
    response_model=PaginatedLogSistemaResponse,
    summary="Listar logs",
    description="Lista logs do sistema com filtros e paginação",
    responses={
        200: {"description": "Lista de logs retornada com sucesso"},
        403: {"model": ErrorResponse, "description": "Sem permissão para acessar logs"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
@rate_limit(max_requests=100, window_seconds=3600)
async def list_logs(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    usuario_id: Optional[int] = Query(None, description="Filtrar por usuário"),
    nivel: Optional[str] = Query(None, description="Filtrar por nível"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    data_inicio: Optional[datetime] = Query(None, description="Data de início"),
    data_fim: Optional[datetime] = Query(None, description="Data de fim"),
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Lista logs do sistema com filtros e paginação.
    """
    log_service = LogSistemaService(db)
    
    skip = (page - 1) * size
    
    logs = await log_service.list_logs(
        skip=skip,
        limit=size,
        usuario_id=usuario_id,
        nivel=nivel,
        categoria=categoria,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    total = len(logs)  # TODO: Implementar count
    
    return PaginatedLogSistemaResponse(
        items=logs,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


# Rotas para configurações
@router.get(
    "/configuracoes",
    response_model=PaginatedConfiguracaoSistemaResponse,
    summary="Listar configurações",
    description="Lista configurações do sistema com filtros e paginação",
    responses={
        200: {"description": "Lista de configurações retornada com sucesso"},
        403: {"model": ErrorResponse, "description": "Sem permissão para acessar configurações"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
@rate_limit(max_requests=100, window_seconds=3600)
async def list_configuracoes(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Tamanho da página"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Lista configurações do sistema com filtros e paginação.
    """
    config_service = ConfiguracaoSistemaService(db)
    
    skip = (page - 1) * size
    
    configs = await config_service.list_configuracoes(
        skip=skip,
        limit=size,
        categoria=categoria,
        ativo=ativo
    )
    
    total = len(configs)  # TODO: Implementar count
    
    return PaginatedConfiguracaoSistemaResponse(
        items=configs,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post(
    "/configuracoes",
    response_model=ConfiguracaoSistemaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar configuração",
    description="Cria uma nova configuração do sistema",
    responses={
        201: {"description": "Configuração criada com sucesso"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        403: {"model": ErrorResponse, "description": "Sem permissão para criar configuração"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
@rate_limit(max_requests=10, window_seconds=3600)
async def create_configuracao(
    config_data: ConfiguracaoSistemaCreate,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Cria uma nova configuração do sistema.
    """
    config_service = ConfiguracaoSistemaService(db)
    
    config = await config_service.create_configuracao(config_data)
    
    return config


@router.put(
    "/configuracoes/{chave}",
    response_model=ConfiguracaoSistemaResponse,
    summary="Atualizar configuração",
    description="Atualiza uma configuração do sistema",
    responses={
        200: {"description": "Configuração atualizada com sucesso"},
        404: {"model": ErrorResponse, "description": "Configuração não encontrada"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        403: {"model": ErrorResponse, "description": "Sem permissão para atualizar configuração"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
@rate_limit(max_requests=20, window_seconds=3600)
async def update_configuracao(
    chave: str,
    config_data: ConfiguracaoSistemaUpdate,
    current_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza uma configuração do sistema.
    """
    config_service = ConfiguracaoSistemaService(db)
    
    config = await config_service.update_configuracao(chave, config_data)
    
    return config
