"""
Schemas para usuários e autenticação
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator

from .common import PaginatedResponse


class UsuarioBase(BaseModel):
    """Schema base para usuário"""
    username: str = Field(..., description="Nome de usuário único")
    email: EmailStr = Field(..., description="Email do usuário")
    nome_completo: str = Field(..., description="Nome completo")
    cargo: Optional[str] = Field(None, description="Cargo do usuário")
    departamento: Optional[str] = Field(None, description="Departamento")
    telefone: Optional[str] = Field(None, description="Telefone")
    orgao_cnpj: Optional[str] = Field(None, description="CNPJ do órgão")
    orgao_nome: Optional[str] = Field(None, description="Nome do órgão")
    unidade_codigo: Optional[str] = Field(None, description="Código da unidade")
    unidade_nome: Optional[str] = Field(None, description="Nome da unidade")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username deve ter pelo menos 3 caracteres')
        return v.lower()


class UsuarioCreate(UsuarioBase):
    """Schema para criação de usuário"""
    senha: str = Field(..., min_length=8, description="Senha do usuário")
    confirmar_senha: str = Field(..., description="Confirmação da senha")
    is_admin: bool = Field(False, description="Se é administrador")
    is_gestor: bool = Field(False, description="Se é gestor")
    is_operador: bool = Field(True, description="Se é operador")
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        if self.confirmar_senha != self.senha:
            raise ValueError('Senhas não coincidem')
        return self


class UsuarioUpdate(BaseModel):
    """Schema para atualização de usuário"""
    email: Optional[EmailStr] = None
    nome_completo: Optional[str] = None
    cargo: Optional[str] = None
    departamento: Optional[str] = None
    telefone: Optional[str] = None
    orgao_cnpj: Optional[str] = None
    orgao_nome: Optional[str] = None
    unidade_codigo: Optional[str] = None
    unidade_nome: Optional[str] = None
    ativo: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_gestor: Optional[bool] = None
    is_operador: Optional[bool] = None


class UsuarioResponse(BaseModel):
    """Schema para resposta de usuário"""
    id: int
    username: str
    email: str
    nome_completo: str
    cargo: Optional[str] = None
    departamento: Optional[str] = None
    telefone: Optional[str] = None
    orgao_cnpj: Optional[str] = None
    orgao_nome: Optional[str] = None
    unidade_codigo: Optional[str] = None
    unidade_nome: Optional[str] = None
    ativo: bool
    is_admin: bool
    is_gestor: bool
    is_operador: bool
    ultimo_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class UsuarioLogin(BaseModel):
    """Schema para login"""
    username: str = Field(..., description="Username ou email")
    password: str = Field(..., description="Senha")


class TokenResponse(BaseModel):
    """Schema para resposta de token"""
    access_token: str = Field(..., description="Token de acesso")
    token_type: str = Field("bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    user: UsuarioResponse = Field(..., description="Dados do usuário")


class PerfilUsuarioBase(BaseModel):
    """Schema base para perfil de usuário"""
    nome_perfil: str = Field(..., description="Nome do perfil")
    descricao: Optional[str] = Field(None, description="Descrição do perfil")
    pode_consultar_pca: bool = Field(True, description="Pode consultar PCA")
    pode_consultar_contratacao: bool = Field(True, description="Pode consultar contratações")
    pode_consultar_ata: bool = Field(True, description="Pode consultar atas")
    pode_consultar_contrato: bool = Field(True, description="Pode consultar contratos")
    pode_exportar_dados: bool = Field(False, description="Pode exportar dados")
    pode_gerenciar_usuarios: bool = Field(False, description="Pode gerenciar usuários")
    pode_administrar_sistema: bool = Field(False, description="Pode administrar sistema")
    pode_usar_api: bool = Field(True, description="Pode usar API")
    limite_requisicoes_hora: int = Field(1000, description="Limite de requisições por hora")


class PerfilUsuarioCreate(PerfilUsuarioBase):
    """Schema para criação de perfil"""
    pass


class PerfilUsuarioUpdate(BaseModel):
    """Schema para atualização de perfil"""
    nome_perfil: Optional[str] = None
    descricao: Optional[str] = None
    pode_consultar_pca: Optional[bool] = None
    pode_consultar_contratacao: Optional[bool] = None
    pode_consultar_ata: Optional[bool] = None
    pode_consultar_contrato: Optional[bool] = None
    pode_exportar_dados: Optional[bool] = None
    pode_gerenciar_usuarios: Optional[bool] = None
    pode_administrar_sistema: Optional[bool] = None
    pode_usar_api: Optional[bool] = None
    limite_requisicoes_hora: Optional[int] = None
    ativo: Optional[bool] = None


class PerfilUsuarioResponse(BaseModel):
    """Schema para resposta de perfil"""
    id: int
    nome_perfil: str
    descricao: Optional[str] = None
    ativo: bool
    pode_consultar_pca: bool
    pode_consultar_contratacao: bool
    pode_consultar_ata: bool
    pode_consultar_contrato: bool
    pode_exportar_dados: bool
    pode_gerenciar_usuarios: bool
    pode_administrar_sistema: bool
    pode_usar_api: bool
    limite_requisicoes_hora: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class UsuarioPerfilResponse(BaseModel):
    """Schema para resposta de associação usuário-perfil"""
    id: int
    usuario_id: int
    perfil_id: int
    data_atribuicao: Optional[datetime] = None
    data_revogacao: Optional[datetime] = None
    ativo: bool
    motivo_atribuicao: Optional[str] = None
    motivo_revogacao: Optional[str] = None
    usuario: UsuarioResponse
    perfil: PerfilUsuarioResponse
    
    model_config = {"from_attributes": True}


class LogSistemaResponse(BaseModel):
    """Schema para resposta de log do sistema"""
    id: int
    usuario_id: Optional[int] = None
    nivel: str
    categoria: str
    modulo: Optional[str] = None
    mensagem: str
    detalhes: Optional[str] = None
    ip_origem: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    metodo_http: Optional[str] = None
    tempo_processamento: Optional[int] = None
    status_code: Optional[int] = None
    contexto_adicional: Optional[str] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ConfiguracaoSistemaBase(BaseModel):
    """Schema base para configuração do sistema"""
    chave: str = Field(..., description="Chave da configuração")
    valor: Optional[str] = Field(None, description="Valor da configuração")
    tipo: str = Field(..., description="Tipo do valor (STRING, INTEGER, BOOLEAN, JSON)")
    descricao: Optional[str] = Field(None, description="Descrição da configuração")
    categoria: Optional[str] = Field(None, description="Categoria da configuração")
    valor_padrao: Optional[str] = Field(None, description="Valor padrão")
    valor_minimo: Optional[str] = Field(None, description="Valor mínimo")
    valor_maximo: Optional[str] = Field(None, description="Valor máximo")


class ConfiguracaoSistemaCreate(ConfiguracaoSistemaBase):
    """Schema para criação de configuração"""
    pass


class ConfiguracaoSistemaUpdate(BaseModel):
    """Schema para atualização de configuração"""
    valor: Optional[str] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    ativo: Optional[bool] = None
    valor_padrao: Optional[str] = None
    valor_minimo: Optional[str] = None
    valor_maximo: Optional[str] = None


class ConfiguracaoSistemaResponse(BaseModel):
    """Schema para resposta de configuração"""
    id: int
    chave: str
    valor: Optional[str] = None
    tipo: str
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    ativo: bool
    somente_leitura: bool
    valor_padrao: Optional[str] = None
    valor_minimo: Optional[str] = None
    valor_maximo: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    """Schema para mudança de senha"""
    senha_atual: str = Field(..., description="Senha atual")
    senha_nova: str = Field(..., min_length=8, description="Nova senha")
    confirmar_senha_nova: str = Field(..., description="Confirmação da nova senha")
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        if self.confirmar_senha_nova != self.senha_nova:
            raise ValueError('Senhas não coincidem')
        return self


# Pagination responses
class PaginatedUsuarioResponse(PaginatedResponse):
    """Resposta paginada para usuários"""
    items: List[UsuarioResponse]


class PaginatedPerfilUsuarioResponse(PaginatedResponse):
    """Resposta paginada para perfis de usuário"""
    items: List[PerfilUsuarioResponse]


class PaginatedLogSistemaResponse(PaginatedResponse):
    """Resposta paginada para logs do sistema"""
    items: List[LogSistemaResponse]


class PaginatedConfiguracaoSistemaResponse(PaginatedResponse):
    """Resposta paginada para configurações do sistema"""
    items: List[ConfiguracaoSistemaResponse]
