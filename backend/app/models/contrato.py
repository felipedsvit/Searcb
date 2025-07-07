from sqlalchemy import Column, String, Integer, Date, DateTime, Text, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .base import BaseModel, AuditLogModel, SyncLogModel


class Contrato(BaseModel, AuditLogModel, SyncLogModel):
    """Model for Contratos (Contracts)."""
    
    __tablename__ = "contrato"
    
    # PNCP Identification
    numero_controle_pncp = Column(String(50), unique=True, index=True, nullable=False)
    numero_controle_pncp_compra = Column(String(50), index=True, nullable=True)
    numero_contrato_empenho = Column(String(50), nullable=True)
    ano_contrato = Column(Integer, index=True, nullable=False)
    sequencial_contrato = Column(Integer, nullable=True)
    processo = Column(String(50), nullable=True)
    
    # Contract type and category
    tipo_contrato_id = Column(Integer, nullable=True)
    tipo_contrato_nome = Column(String(100), nullable=True)
    categoria_processo_id = Column(Integer, nullable=True)
    categoria_processo_nome = Column(String(100), nullable=True)
    
    # Nature
    receita = Column(Boolean, default=False)
    
    # Object and description
    objeto_contrato = Column(Text, nullable=False)
    informacao_complementar = Column(Text, nullable=True)
    
    # Organization/Entity
    orgao_entidade_cnpj = Column(String(14), index=True, nullable=False)
    orgao_entidade_razao_social = Column(String(255), nullable=False)
    orgao_entidade_poder_id = Column(String(1), nullable=True)
    orgao_entidade_esfera_id = Column(String(1), nullable=True)
    
    # Executing unit
    unidade_orgao_codigo = Column(String(20), nullable=True)
    unidade_orgao_nome = Column(String(255), nullable=True)
    unidade_orgao_codigo_ibge = Column(Integer, nullable=True)
    unidade_orgao_municipio = Column(String(100), nullable=True)
    unidade_orgao_uf_sigla = Column(String(2), nullable=True)
    unidade_orgao_uf_nome = Column(String(50), nullable=True)
    
    # Subrogated organization
    orgao_subrogado_cnpj = Column(String(14), nullable=True)
    orgao_subrogado_razao_social = Column(String(255), nullable=True)
    orgao_subrogado_poder_id = Column(String(1), nullable=True)
    orgao_subrogado_esfera_id = Column(String(1), nullable=True)
    
    # Subrogated unit
    unidade_subrogada_codigo = Column(String(20), nullable=True)
    unidade_subrogada_nome = Column(String(255), nullable=True)
    unidade_subrogada_codigo_ibge = Column(Integer, nullable=True)
    unidade_subrogada_municipio = Column(String(100), nullable=True)
    unidade_subrogada_uf_sigla = Column(String(2), nullable=True)
    unidade_subrogada_uf_nome = Column(String(50), nullable=True)
    
    # Supplier
    tipo_pessoa = Column(String(2), nullable=False)  # PJ, PF
    ni_fornecedor = Column(String(30), nullable=False)  # CNPJ/CPF
    nome_razao_social_fornecedor = Column(String(255), nullable=False)
    
    # Subcontracted (optional)
    tipo_pessoa_subcontratada = Column(String(2), nullable=True)
    ni_fornecedor_subcontratado = Column(String(30), nullable=True)
    nome_fornecedor_subcontratado = Column(String(255), nullable=True)
    
    # Values
    valor_inicial = Column(Numeric(15, 4), nullable=True)
    numero_parcelas = Column(Integer, nullable=True)
    valor_parcela = Column(Numeric(15, 4), nullable=True)
    valor_global = Column(Numeric(15, 4), nullable=True)
    valor_acumulado = Column(Numeric(15, 4), nullable=True)
    
    # Dates
    data_assinatura = Column(Date, nullable=True)
    data_vigencia_inicio = Column(Date, index=True, nullable=True)
    data_vigencia_fim = Column(Date, index=True, nullable=True)
    data_publicacao_pncp = Column(DateTime, nullable=True)
    data_atualizacao = Column(DateTime, nullable=True)
    
    # Additional information
    url_cipi = Column(String(500), nullable=True)
    sistema_origem = Column(String(100), nullable=True)
    usuario_cadastro = Column(String(255), nullable=True)
    
    # Status
    situacao_contrato = Column(String(50), nullable=True)
    motivo_rescisao = Column(Text, nullable=True)
    data_rescisao = Column(Date, nullable=True)
    
    # Relationships
    aditivos = relationship("AditivoContrato", back_populates="contrato", cascade="all, delete-orphan")
    medicoes = relationship("MedicaoContrato", back_populates="contrato", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Contrato(numero_controle_pncp={self.numero_controle_pncp})>"


class AditivoContrato(BaseModel, AuditLogModel):
    """Model for contract amendments."""
    
    __tablename__ = "aditivo_contrato"
    
    # Relationship
    contrato_id = Column(Integer, ForeignKey("contrato.id"), nullable=False)
    contrato = relationship("Contrato", back_populates="aditivos")
    
    # Amendment identification
    numero_aditivo = Column(String(50), nullable=False)
    tipo_aditivo = Column(String(50), nullable=True)  # Prazo, Valor, Objeto
    
    # Dates
    data_assinatura = Column(Date, nullable=True)
    data_vigencia_inicio = Column(Date, nullable=True)
    data_vigencia_fim = Column(Date, nullable=True)
    data_publicacao = Column(Date, nullable=True)
    
    # Values
    valor_aditivo = Column(Numeric(15, 4), nullable=True)
    percentual_aditivo = Column(Numeric(5, 2), nullable=True)
    
    # Description
    objeto_aditivo = Column(Text, nullable=True)
    justificativa = Column(Text, nullable=True)
    
    # Status
    situacao_aditivo = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<AditivoContrato(contrato_id={self.contrato_id}, numero_aditivo={self.numero_aditivo})>"


class MedicaoContrato(BaseModel, AuditLogModel):
    """Model for contract measurements."""
    
    __tablename__ = "medicao_contrato"
    
    # Relationship
    contrato_id = Column(Integer, ForeignKey("contrato.id"), nullable=False)
    contrato = relationship("Contrato", back_populates="medicoes")
    
    # Measurement identification
    numero_medicao = Column(String(50), nullable=False)
    periodo_referencia = Column(String(50), nullable=True)
    
    # Dates
    data_inicio_periodo = Column(Date, nullable=True)
    data_fim_periodo = Column(Date, nullable=True)
    data_medicao = Column(Date, nullable=True)
    data_vencimento = Column(Date, nullable=True)
    
    # Values
    valor_medicao = Column(Numeric(15, 4), nullable=True)
    percentual_execucao = Column(Numeric(5, 2), nullable=True)
    
    # Description
    descricao_medicao = Column(Text, nullable=True)
    observacoes = Column(Text, nullable=True)
    
    # Status
    situacao_medicao = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<MedicaoContrato(contrato_id={self.contrato_id}, numero_medicao={self.numero_medicao})>"


class GarantiaContrato(BaseModel, AuditLogModel):
    """Model for contract guarantees."""
    
    __tablename__ = "garantia_contrato"
    
    # Relationship
    contrato_id = Column(Integer, ForeignKey("contrato.id"), nullable=False)
    contrato = relationship("Contrato")
    
    # Guarantee identification
    tipo_garantia = Column(String(50), nullable=False)  # Caução, Fiança, Seguro
    numero_garantia = Column(String(50), nullable=True)
    
    # Values
    valor_garantia = Column(Numeric(15, 4), nullable=True)
    percentual_garantia = Column(Numeric(5, 2), nullable=True)
    
    # Dates
    data_inicio_vigencia = Column(Date, nullable=True)
    data_fim_vigencia = Column(Date, nullable=True)
    
    # Institution
    instituicao_garantidora = Column(String(255), nullable=True)
    cnpj_instituicao = Column(String(14), nullable=True)
    
    # Status
    situacao_garantia = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<GarantiaContrato(contrato_id={self.contrato_id}, tipo_garantia={self.tipo_garantia})>"
