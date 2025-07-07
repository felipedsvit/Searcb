from sqlalchemy import Column, String, Integer, Date, DateTime, Text, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .base import BaseModel, AuditLogModel, SyncLogModel


class Contratacao(BaseModel, AuditLogModel, SyncLogModel):
    """Model for Contratações (Contracting processes)."""
    
    __tablename__ = "contratacao"
    
    # PNCP Identification
    numero_controle_pncp = Column(String(50), unique=True, index=True, nullable=False)
    numero_compra = Column(String(50), nullable=True)
    ano_compra = Column(Integer, index=True, nullable=False)
    processo = Column(String(50), nullable=True)
    sequencial_compra = Column(Integer, nullable=True)
    
    # Instrument and modality
    tipo_instrumento_convocatorio_id = Column(Integer, nullable=True)
    tipo_instrumento_convocatorio_nome = Column(String(100), nullable=True)
    modalidade_id = Column(Integer, index=True, nullable=False)
    modalidade_nome = Column(String(100), nullable=False)
    modo_disputa_id = Column(Integer, nullable=True)
    modo_disputa_nome = Column(String(100), nullable=True)
    
    # Judgment criteria
    criterio_julgamento_id = Column(Integer, nullable=True)
    criterio_julgamento_nome = Column(String(100), nullable=True)
    
    # Status
    situacao_compra_id = Column(Integer, index=True, nullable=False)
    situacao_compra_nome = Column(String(100), nullable=False)
    
    # Object and description
    objeto_compra = Column(Text, nullable=False)
    informacao_complementar = Column(Text, nullable=True)
    srp = Column(Boolean, default=False)  # Sistema de Registro de Preços
    
    # Legal basis
    amparo_legal_codigo = Column(Integer, nullable=True)
    amparo_legal_nome = Column(String(255), nullable=True)
    amparo_legal_descricao = Column(Text, nullable=True)
    
    # Values
    valor_total_estimado = Column(Numeric(15, 4), nullable=True)
    valor_total_homologado = Column(Numeric(15, 4), nullable=True)
    valor_total_adjudicado = Column(Numeric(15, 4), nullable=True)
    
    # Dates
    data_abertura_proposta = Column(DateTime, nullable=True)
    data_encerramento_proposta = Column(DateTime, index=True, nullable=True)
    data_publicacao_pncp = Column(Date, index=True, nullable=True)
    data_inclusao = Column(Date, nullable=True)
    data_atualizacao = Column(Date, nullable=True)
    data_homologacao = Column(Date, nullable=True)
    data_adjudicacao = Column(Date, nullable=True)
    
    # Organization/Entity
    orgao_entidade_cnpj = Column(String(14), index=True, nullable=False)
    orgao_entidade_razao_social = Column(String(255), nullable=False)
    orgao_entidade_poder_id = Column(String(1), nullable=True)
    orgao_entidade_esfera_id = Column(String(1), nullable=True)
    orgao_entidade_natureza_juridica_id = Column(Integer, nullable=True)
    
    # Unit/Department
    unidade_orgao_codigo = Column(String(20), nullable=True)
    unidade_orgao_nome = Column(String(255), nullable=True)
    unidade_orgao_codigo_ibge = Column(Integer, nullable=True)
    unidade_orgao_municipio = Column(String(100), nullable=True)
    unidade_orgao_uf_sigla = Column(String(2), index=True, nullable=True)
    unidade_orgao_uf_nome = Column(String(50), nullable=True)
    
    # Subrogated organization (optional)
    orgao_subrogado_cnpj = Column(String(14), nullable=True)
    orgao_subrogado_razao_social = Column(String(255), nullable=True)
    orgao_subrogado_poder_id = Column(String(1), nullable=True)
    orgao_subrogado_esfera_id = Column(String(1), nullable=True)
    
    # Subrogated unit (optional)
    unidade_subrogada_codigo = Column(String(20), nullable=True)
    unidade_subrogada_nome = Column(String(255), nullable=True)
    unidade_subrogada_codigo_ibge = Column(Integer, nullable=True)
    unidade_subrogada_municipio = Column(String(100), nullable=True)
    unidade_subrogada_uf_sigla = Column(String(2), nullable=True)
    unidade_subrogada_uf_nome = Column(String(50), nullable=True)
    
    # System and user info
    usuario_nome = Column(String(255), nullable=True)
    link_sistema_origem = Column(String(500), nullable=True)
    justificativa_presencial = Column(Text, nullable=True)
    
    # Additional fields
    possui_orcamento_sigiloso = Column(Boolean, default=False)
    valor_orcamento_sigiloso = Column(Numeric(15, 4), nullable=True)
    
    # Relationships
    itens = relationship("ItemContratacao", back_populates="contratacao", cascade="all, delete-orphan")
    participantes = relationship("ParticipanteContratacao", back_populates="contratacao", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Contratacao(numero_controle_pncp={self.numero_controle_pncp})>"


class ItemContratacao(BaseModel, AuditLogModel):
    """Model for contracting items."""
    
    __tablename__ = "item_contratacao"
    
    # Relationship
    contratacao_id = Column(Integer, ForeignKey("contratacao.id"), nullable=False)
    contratacao = relationship("Contratacao", back_populates="itens")
    
    # Item identification
    numero_item = Column(Integer, nullable=False)
    descricao_item = Column(Text, nullable=False)
    unidade_medida = Column(String(20), nullable=True)
    
    # Classification
    classificacao_catalogo_id = Column(String(10), nullable=True)
    nome_classificacao_catalogo = Column(String(50), nullable=True)
    
    # Quantities and values
    quantidade = Column(Numeric(15, 4), nullable=True)
    valor_unitario = Column(Numeric(15, 4), nullable=True)
    valor_total = Column(Numeric(15, 4), nullable=True)
    valor_unitario_homologado = Column(Numeric(15, 4), nullable=True)
    valor_total_homologado = Column(Numeric(15, 4), nullable=True)
    
    # Status
    situacao_item_id = Column(Integer, nullable=True)
    situacao_item_nome = Column(String(100), nullable=True)
    
    # Benefits
    tipo_beneficio_id = Column(Integer, nullable=True)
    tipo_beneficio_nome = Column(String(100), nullable=True)
    
    # Winner information
    fornecedor_vencedor_cnpj = Column(String(14), nullable=True)
    fornecedor_vencedor_nome = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<ItemContratacao(contratacao_id={self.contratacao_id}, numero_item={self.numero_item})>"


class ParticipanteContratacao(BaseModel):
    """Model for contracting participants."""
    
    __tablename__ = "participante_contratacao"
    
    # Relationship
    contratacao_id = Column(Integer, ForeignKey("contratacao.id"), nullable=False)
    contratacao = relationship("Contratacao", back_populates="participantes")
    
    # Participant identification
    tipo_pessoa = Column(String(2), nullable=False)  # PJ, PF
    ni_participante = Column(String(30), nullable=False)  # CNPJ/CPF
    nome_razao_social = Column(String(255), nullable=False)
    
    # Company information
    porte_empresa_id = Column(Integer, nullable=True)
    porte_empresa_nome = Column(String(50), nullable=True)
    natureza_juridica_id = Column(Integer, nullable=True)
    natureza_juridica_nome = Column(String(100), nullable=True)
    
    # Participation details
    situacao_participacao = Column(String(50), nullable=True)  # Habilitado, Desabilitado, Vencedor
    valor_proposta = Column(Numeric(15, 4), nullable=True)
    data_proposta = Column(DateTime, nullable=True)
    
    # ME/EPP benefits
    declara_me_epp = Column(Boolean, default=False)
    declara_coop = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<ParticipanteContratacao(contratacao_id={self.contratacao_id}, ni={self.ni_participante})>"
