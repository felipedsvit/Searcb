from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Usuario(BaseModel):
    """Model for system users."""
    
    __tablename__ = "usuario"
    
    # User identification
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    nome_completo = Column(String(255), nullable=False)
    
    # Authentication
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)
    
    # Profile information
    cargo = Column(String(100), nullable=True)
    departamento = Column(String(100), nullable=True)
    telefone = Column(String(20), nullable=True)
    
    # Organization
    orgao_cnpj = Column(String(14), nullable=True)
    orgao_nome = Column(String(255), nullable=True)
    unidade_codigo = Column(String(20), nullable=True)
    unidade_nome = Column(String(255), nullable=True)
    
    # Permissions
    is_admin = Column(Boolean, default=False)
    is_gestor = Column(Boolean, default=False)
    is_operador = Column(Boolean, default=False)
    
    # System integration
    id_usuario_pncp = Column(Integer, nullable=True)
    token_pncp = Column(String(500), nullable=True)
    
    # Activity tracking
    ultimo_login = Column(DateTime, nullable=True)
    data_expiracao_senha = Column(DateTime, nullable=True)
    tentativas_login = Column(Integer, default=0)
    
    # Relationships
    logs_sistema = relationship("LogSistema", back_populates="usuario")
    
    def __repr__(self):
        return f"<Usuario(username={self.username}, email={self.email})>"


class PerfilUsuario(BaseModel):
    """Model for user profiles and permissions."""
    
    __tablename__ = "perfil_usuario"
    
    # Profile identification
    nome_perfil = Column(String(100), unique=True, nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Status
    ativo = Column(Boolean, default=True)
    
    # System permissions
    pode_consultar_pca = Column(Boolean, default=True)
    pode_consultar_contratacao = Column(Boolean, default=True)
    pode_consultar_ata = Column(Boolean, default=True)
    pode_consultar_contrato = Column(Boolean, default=True)
    pode_exportar_dados = Column(Boolean, default=False)
    pode_gerenciar_usuarios = Column(Boolean, default=False)
    pode_administrar_sistema = Column(Boolean, default=False)
    
    # API permissions
    pode_usar_api = Column(Boolean, default=True)
    limite_requisicoes_hora = Column(Integer, default=1000)
    
    def __repr__(self):
        return f"<PerfilUsuario(nome_perfil={self.nome_perfil})>"


class UsuarioPerfil(BaseModel):
    """Model for user-profile associations."""
    
    __tablename__ = "usuario_perfil"
    
    # Relationships
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)
    perfil_id = Column(Integer, ForeignKey("perfil_usuario.id"), nullable=False)
    
    # User and profile relationships
    usuario = relationship("Usuario")
    perfil = relationship("PerfilUsuario")
    
    # Assignment details
    data_atribuicao = Column(DateTime, nullable=True)
    data_revogacao = Column(DateTime, nullable=True)
    ativo = Column(Boolean, default=True)
    
    # Assignment reason
    motivo_atribuicao = Column(Text, nullable=True)
    motivo_revogacao = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<UsuarioPerfil(usuario_id={self.usuario_id}, perfil_id={self.perfil_id})>"


class LogSistema(BaseModel):
    """Model for system logs."""
    
    __tablename__ = "log_sistema"
    
    # Relationship
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=True)
    usuario = relationship("Usuario", back_populates="logs_sistema")
    
    # Log identification
    nivel = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    categoria = Column(String(50), nullable=False)  # AUTH, API, SYNC, SYSTEM
    modulo = Column(String(100), nullable=True)
    
    # Log content
    mensagem = Column(Text, nullable=False)
    detalhes = Column(Text, nullable=True)
    
    # Request information
    ip_origem = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    endpoint = Column(String(200), nullable=True)
    metodo_http = Column(String(10), nullable=True)
    
    # Performance metrics
    tempo_processamento = Column(Integer, nullable=True)  # milliseconds
    status_code = Column(Integer, nullable=True)
    
    # Additional context
    contexto_adicional = Column(Text, nullable=True)  # JSON string
    
    def __repr__(self):
        return f"<LogSistema(nivel={self.nivel}, categoria={self.categoria}, created_at={self.created_at})>"


class ConfiguracaoSistema(BaseModel):
    """Model for system configurations."""
    
    __tablename__ = "configuracao_sistema"
    
    # Configuration identification
    chave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text, nullable=True)
    tipo = Column(String(20), nullable=False)  # STRING, INTEGER, BOOLEAN, JSON
    
    # Configuration details
    descricao = Column(Text, nullable=True)
    categoria = Column(String(50), nullable=True)
    
    # Status
    ativo = Column(Boolean, default=True)
    somente_leitura = Column(Boolean, default=False)
    
    # Validation
    valor_padrao = Column(Text, nullable=True)
    valor_minimo = Column(Text, nullable=True)
    valor_maximo = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ConfiguracaoSistema(chave={self.chave}, valor={self.valor})>"
