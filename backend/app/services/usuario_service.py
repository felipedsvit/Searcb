"""
Serviço para gestão de usuários
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
import logging

from app.models.usuario import Usuario, PerfilUsuario, UsuarioPerfil, LogSistema, ConfiguracaoSistema
from app.schemas.usuario import (
    UsuarioCreate, UsuarioUpdate, PerfilUsuarioCreate, PerfilUsuarioUpdate,
    ConfiguracaoSistemaCreate, ConfiguracaoSistemaUpdate, ChangePasswordRequest
)
from app.core.security import SecurityService
from app.core.cache import get_cache, set_cache, delete_cache
from app.utils.helpers import generate_uuid

logger = logging.getLogger(__name__)
security_service = SecurityService()


class UsuarioService:
    """
    Serviço para operações de usuário
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_usuario_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """
        Obtém usuário por ID
        """
        cache_key = f"usuario:{usuario_id}"
        cached_usuario = await get_cache(cache_key)
        
        if cached_usuario:
            return cached_usuario
        
        usuario = self.db.query(Usuario).filter(
            and_(Usuario.id == usuario_id, Usuario.deleted_at.is_(None))
        ).first()
        
        if usuario:
            await set_cache(cache_key, usuario, expire=3600)
        
        return usuario
    
    async def get_usuario_by_username(self, username: str) -> Optional[Usuario]:
        """
        Obtém usuário por username
        """
        cache_key = f"usuario:username:{username}"
        cached_usuario = await get_cache(cache_key)
        
        if cached_usuario:
            return cached_usuario
        
        usuario = self.db.query(Usuario).filter(
            and_(
                Usuario.username == username,
                Usuario.deleted_at.is_(None)
            )
        ).first()
        
        if usuario:
            await set_cache(cache_key, usuario, expire=3600)
        
        return usuario
    
    async def get_usuario_by_email(self, email: str) -> Optional[Usuario]:
        """
        Obtém usuário por email
        """
        cache_key = f"usuario:email:{email}"
        cached_usuario = await get_cache(cache_key)
        
        if cached_usuario:
            return cached_usuario
        
        usuario = self.db.query(Usuario).filter(
            and_(
                Usuario.email == email,
                Usuario.deleted_at.is_(None)
            )
        ).first()
        
        if usuario:
            await set_cache(cache_key, usuario, expire=3600)
        
        return usuario
    
    async def create_usuario(self, usuario_data: UsuarioCreate) -> Usuario:
        """
        Cria novo usuário
        """
        # Verificar se username já existe
        existing_username = await self.get_usuario_by_username(usuario_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já cadastrado"
            )
        
        # Verificar se email já existe
        existing_email = await self.get_usuario_by_email(usuario_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Hash da senha
        senha_hash = security_service.get_password_hash(usuario_data.senha)
        
        # Criar usuário
        usuario = Usuario(
            username=usuario_data.username,
            email=usuario_data.email,
            nome_completo=usuario_data.nome_completo,
            senha_hash=senha_hash,
            cargo=usuario_data.cargo,
            departamento=usuario_data.departamento,
            telefone=usuario_data.telefone,
            orgao_cnpj=usuario_data.orgao_cnpj,
            orgao_nome=usuario_data.orgao_nome,
            unidade_codigo=usuario_data.unidade_codigo,
            unidade_nome=usuario_data.unidade_nome,
            is_admin=usuario_data.is_admin,
            is_gestor=usuario_data.is_gestor,
            is_operador=usuario_data.is_operador,
            ativo=True,
            created_at=datetime.utcnow()
        )
        
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        
        # Limpar cache
        await delete_cache(f"usuario:username:{usuario.username}")
        await delete_cache(f"usuario:email:{usuario.email}")
        
        logger.info(f"Usuário criado: {usuario.username}")
        return usuario
    
    async def update_usuario(self, usuario_id: int, usuario_data: UsuarioUpdate) -> Usuario:
        """
        Atualiza usuário
        """
        usuario = await self.get_usuario_by_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar se email está sendo alterado e se já existe
        if usuario_data.email and usuario_data.email != usuario.email:
            existing_email = await self.get_usuario_by_email(usuario_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado"
                )
        
        # Atualizar campos
        for field, value in usuario_data.dict(exclude_unset=True).items():
            setattr(usuario, field, value)
        
        usuario.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(usuario)
        
        # Limpar cache
        await delete_cache(f"usuario:{usuario_id}")
        if usuario_data.email:
            await delete_cache(f"usuario:email:{usuario.email}")
        
        logger.info(f"Usuário atualizado: {usuario.username}")
        return usuario
    
    async def delete_usuario(self, usuario_id: int) -> bool:
        """
        Soft delete de usuário
        """
        usuario = await self.get_usuario_by_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        usuario.soft_delete()
        self.db.commit()
        
        # Limpar cache
        await delete_cache(f"usuario:{usuario_id}")
        await delete_cache(f"usuario:username:{usuario.username}")
        await delete_cache(f"usuario:email:{usuario.email}")
        
        logger.info(f"Usuário removido: {usuario.username}")
        return True
    
    async def change_password(self, usuario_id: int, password_data: ChangePasswordRequest) -> bool:
        """
        Altera senha do usuário
        """
        usuario = await self.get_usuario_by_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar senha atual
        if not security_service.verify_password(password_data.senha_atual, usuario.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )
        
        # Atualizar senha
        usuario.senha_hash = security_service.get_password_hash(password_data.senha_nova)
        usuario.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Limpar cache
        await delete_cache(f"usuario:{usuario_id}")
        
        logger.info(f"Senha alterada para usuário: {usuario.username}")
        return True
    
    async def authenticate_usuario(self, username: str, password: str) -> Optional[Usuario]:
        """
        Autentica usuário
        """
        # Buscar por username ou email
        usuario = self.db.query(Usuario).filter(
            and_(
                or_(
                    Usuario.username == username,
                    Usuario.email == username
                ),
                Usuario.deleted_at.is_(None),
                Usuario.ativo == True
            )
        ).first()
        
        if not usuario:
            return None
        
        # Verificar senha
        if not security_service.verify_password(password, usuario.senha_hash):
            # Incrementar tentativas de login
            usuario.tentativas_login += 1
            self.db.commit()
            return None
        
        # Reset tentativas e atualizar último login
        usuario.tentativas_login = 0
        usuario.ultimo_login = datetime.utcnow()
        self.db.commit()
        
        return usuario
    
    async def list_usuarios(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        ativo: Optional[bool] = None,
        is_admin: Optional[bool] = None,
        orgao_cnpj: Optional[str] = None
    ) -> List[Usuario]:
        """
        Lista usuários com filtros
        """
        query = self.db.query(Usuario).filter(Usuario.deleted_at.is_(None))
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    Usuario.username.ilike(f"%{search}%"),
                    Usuario.email.ilike(f"%{search}%"),
                    Usuario.nome_completo.ilike(f"%{search}%")
                )
            )
        
        if ativo is not None:
            query = query.filter(Usuario.ativo == ativo)
        
        if is_admin is not None:
            query = query.filter(Usuario.is_admin == is_admin)
        
        if orgao_cnpj:
            query = query.filter(Usuario.orgao_cnpj == orgao_cnpj)
        
        return query.offset(skip).limit(limit).all()
    
    async def count_usuarios(
        self,
        search: Optional[str] = None,
        ativo: Optional[bool] = None,
        is_admin: Optional[bool] = None,
        orgao_cnpj: Optional[str] = None
    ) -> int:
        """
        Conta usuários com filtros
        """
        query = self.db.query(func.count(Usuario.id)).filter(Usuario.deleted_at.is_(None))
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    Usuario.username.ilike(f"%{search}%"),
                    Usuario.email.ilike(f"%{search}%"),
                    Usuario.nome_completo.ilike(f"%{search}%")
                )
            )
        
        if ativo is not None:
            query = query.filter(Usuario.ativo == ativo)
        
        if is_admin is not None:
            query = query.filter(Usuario.is_admin == is_admin)
        
        if orgao_cnpj:
            query = query.filter(Usuario.orgao_cnpj == orgao_cnpj)
        
        return query.scalar()


class PerfilUsuarioService:
    """
    Serviço para perfis de usuário
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_perfil_by_id(self, perfil_id: int) -> Optional[PerfilUsuario]:
        """
        Obtém perfil por ID
        """
        return self.db.query(PerfilUsuario).filter(
            and_(PerfilUsuario.id == perfil_id, PerfilUsuario.deleted_at.is_(None))
        ).first()
    
    async def create_perfil(self, perfil_data: PerfilUsuarioCreate) -> PerfilUsuario:
        """
        Cria novo perfil
        """
        # Verificar se nome do perfil já existe
        existing_perfil = self.db.query(PerfilUsuario).filter(
            and_(
                PerfilUsuario.nome_perfil == perfil_data.nome_perfil,
                PerfilUsuario.deleted_at.is_(None)
            )
        ).first()
        
        if existing_perfil:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome do perfil já existe"
            )
        
        perfil = PerfilUsuario(**perfil_data.dict(), created_at=datetime.utcnow())
        self.db.add(perfil)
        self.db.commit()
        self.db.refresh(perfil)
        
        logger.info(f"Perfil criado: {perfil.nome_perfil}")
        return perfil
    
    async def list_perfis(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> List[PerfilUsuario]:
        """
        Lista perfis com filtros
        """
        query = self.db.query(PerfilUsuario).filter(PerfilUsuario.deleted_at.is_(None))
        
        if search:
            query = query.filter(
                or_(
                    PerfilUsuario.nome_perfil.ilike(f"%{search}%"),
                    PerfilUsuario.descricao.ilike(f"%{search}%")
                )
            )
        
        if ativo is not None:
            query = query.filter(PerfilUsuario.ativo == ativo)
        
        return query.offset(skip).limit(limit).all()


class LogSistemaService:
    """
    Serviço para logs do sistema
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_log(
        self,
        usuario_id: Optional[int],
        nivel: str,
        categoria: str,
        mensagem: str,
        modulo: Optional[str] = None,
        detalhes: Optional[str] = None,
        ip_origem: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        metodo_http: Optional[str] = None,
        tempo_processamento: Optional[int] = None,
        status_code: Optional[int] = None,
        contexto_adicional: Optional[str] = None
    ) -> LogSistema:
        """
        Cria novo log
        """
        log = LogSistema(
            usuario_id=usuario_id,
            nivel=nivel,
            categoria=categoria,
            mensagem=mensagem,
            modulo=modulo,
            detalhes=detalhes,
            ip_origem=ip_origem,
            user_agent=user_agent,
            endpoint=endpoint,
            metodo_http=metodo_http,
            tempo_processamento=tempo_processamento,
            status_code=status_code,
            contexto_adicional=contexto_adicional,
            created_at=datetime.utcnow()
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    async def list_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        usuario_id: Optional[int] = None,
        nivel: Optional[str] = None,
        categoria: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None
    ) -> List[LogSistema]:
        """
        Lista logs com filtros
        """
        query = self.db.query(LogSistema)
        
        if usuario_id:
            query = query.filter(LogSistema.usuario_id == usuario_id)
        
        if nivel:
            query = query.filter(LogSistema.nivel == nivel)
        
        if categoria:
            query = query.filter(LogSistema.categoria == categoria)
        
        if data_inicio:
            query = query.filter(LogSistema.created_at >= data_inicio)
        
        if data_fim:
            query = query.filter(LogSistema.created_at <= data_fim)
        
        return query.order_by(LogSistema.created_at.desc()).offset(skip).limit(limit).all()


class ConfiguracaoSistemaService:
    """
    Serviço para configurações do sistema
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_configuracao_by_chave(self, chave: str) -> Optional[ConfiguracaoSistema]:
        """
        Obtém configuração por chave
        """
        cache_key = f"config:{chave}"
        cached_config = await get_cache(cache_key)
        
        if cached_config:
            return cached_config
        
        config = self.db.query(ConfiguracaoSistema).filter(
            and_(
                ConfiguracaoSistema.chave == chave,
                ConfiguracaoSistema.deleted_at.is_(None),
                ConfiguracaoSistema.ativo == True
            )
        ).first()
        
        if config:
            await set_cache(cache_key, config, expire=3600)
        
        return config
    
    async def create_configuracao(self, config_data: ConfiguracaoSistemaCreate) -> ConfiguracaoSistema:
        """
        Cria nova configuração
        """
        # Verificar se chave já existe
        existing_config = self.db.query(ConfiguracaoSistema).filter(
            and_(
                ConfiguracaoSistema.chave == config_data.chave,
                ConfiguracaoSistema.deleted_at.is_(None)
            )
        ).first()
        
        if existing_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chave de configuração já existe"
            )
        
        config = ConfiguracaoSistema(**config_data.dict(), created_at=datetime.utcnow())
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        
        # Limpar cache
        await delete_cache(f"config:{config.chave}")
        
        logger.info(f"Configuração criada: {config.chave}")
        return config
    
    async def update_configuracao(self, chave: str, config_data: ConfiguracaoSistemaUpdate) -> ConfiguracaoSistema:
        """
        Atualiza configuração
        """
        config = await self.get_configuracao_by_chave(chave)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuração não encontrada"
            )
        
        if config.somente_leitura:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Configuração é somente leitura"
            )
        
        # Atualizar campos
        for field, value in config_data.dict(exclude_unset=True).items():
            setattr(config, field, value)
        
        config.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(config)
        
        # Limpar cache
        await delete_cache(f"config:{config.chave}")
        
        logger.info(f"Configuração atualizada: {config.chave}")
        return config
    
    async def list_configuracoes(
        self,
        skip: int = 0,
        limit: int = 100,
        categoria: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> List[ConfiguracaoSistema]:
        """
        Lista configurações com filtros
        """
        query = self.db.query(ConfiguracaoSistema).filter(ConfiguracaoSistema.deleted_at.is_(None))
        
        if categoria:
            query = query.filter(ConfiguracaoSistema.categoria == categoria)
        
        if ativo is not None:
            query = query.filter(ConfiguracaoSistema.ativo == ativo)
        
        return query.offset(skip).limit(limit).all()
