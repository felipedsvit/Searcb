from sqlalchemy import Column, String, Integer, Date, Boolean, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .base import BaseModel, AuditLogModel, SyncLogModel


class AtaRegistroPreco(BaseModel, AuditLogModel, SyncLogModel):
    """Model for Ata de Registro de Preços (Price Registration Record)."""
    
    __tablename__ = "ata_registro_preco"
    
    # PNCP Identification
    numero_controle_pncp_ata = Column(String(50), unique=True, index=True, nullable=False)
    numero_controle_pncp_compra = Column(String(50), index=True, nullable=True)
    numero_ata_registro_preco = Column(String(50), nullable=True)
    ano_ata = Column(Integer, index=True, nullable=False)
    
    # Dates
    data_assinatura = Column(Date, nullable=True)
    vigencia_inicio = Column(Date, index=True, nullable=True)
    vigencia_fim = Column(Date, index=True, nullable=True)
    data_cancelamento = Column(Date, nullable=True)
    cancelado = Column(Boolean, default=False)
    data_publicacao_pncp = Column(Date, nullable=True)
    data_inclusao = Column(Date, nullable=True)
    data_atualizacao = Column(Date, nullable=True)
    
    # Object and description
    objeto_contratacao = Column(Text, nullable=False)
    informacao_complementar = Column(Text, nullable=True)
    
    # Values
    valor_total_estimado = Column(Numeric(15, 4), nullable=True)
    valor_total_homologado = Column(Numeric(15, 4), nullable=True)
    
    # Organization
    cnpj_orgao = Column(String(14), index=True, nullable=False)
    nome_orgao = Column(String(255), nullable=False)
    codigo_unidade_orgao = Column(String(20), nullable=True)
    nome_unidade_orgao = Column(String(255), nullable=True)
    
    # Subrogated organization (optional)
    cnpj_orgao_subrogado = Column(String(14), nullable=True)
    nome_orgao_subrogado = Column(String(255), nullable=True)
    codigo_unidade_orgao_subrogado = Column(String(20), nullable=True)
    nome_unidade_orgao_subrogado = Column(String(255), nullable=True)
    
    # System info
    usuario = Column(String(255), nullable=True)
    sistema_origem = Column(String(100), nullable=True)
    
    # Status
    situacao_ata = Column(String(50), nullable=True)
    motivo_cancelamento = Column(Text, nullable=True)
    
    # Relationships
    itens = relationship("ItemAtaRegistroPreco", back_populates="ata", cascade="all, delete-orphan")
    fornecedores = relationship("FornecedorAtaRegistroPreco", back_populates="ata", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AtaRegistroPreco(numero_controle_pncp_ata={self.numero_controle_pncp_ata})>"


class ItemAtaRegistroPreco(BaseModel, AuditLogModel):
    """Model for items in Price Registration Records."""
    
    __tablename__ = "item_ata_registro_preco"
    
    # Relationship
    ata_id = Column(Integer, ForeignKey("ata_registro_preco.id"), nullable=False)
    ata = relationship("AtaRegistroPreco", back_populates="itens")
    
    # Item identification
    numero_item = Column(Integer, nullable=False)
    descricao_item = Column(Text, nullable=False)
    unidade_medida = Column(String(20), nullable=True)
    
    # Classification
    classificacao_catalogo_id = Column(String(10), nullable=True)
    nome_classificacao_catalogo = Column(String(50), nullable=True)
    
    # Quantities and values
    quantidade_estimada = Column(Numeric(15, 4), nullable=True)
    valor_unitario = Column(Numeric(15, 4), nullable=True)
    valor_total = Column(Numeric(15, 4), nullable=True)
    valor_unitario_homologado = Column(Numeric(15, 4), nullable=True)
    valor_total_homologado = Column(Numeric(15, 4), nullable=True)
    
    # Status
    situacao_item = Column(String(50), nullable=True)
    
    # Winner information
    fornecedor_vencedor_cnpj = Column(String(14), nullable=True)
    fornecedor_vencedor_nome = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<ItemAtaRegistroPreco(ata_id={self.ata_id}, numero_item={self.numero_item})>"


class FornecedorAtaRegistroPreco(BaseModel):
    """Model for suppliers in Price Registration Records."""
    
    __tablename__ = "fornecedor_ata_registro_preco"
    
    # Relationship
    ata_id = Column(Integer, ForeignKey("ata_registro_preco.id"), nullable=False)
    ata = relationship("AtaRegistroPreco", back_populates="fornecedores")
    
    # Supplier identification
    tipo_pessoa = Column(String(2), nullable=False)  # PJ, PF
    ni_fornecedor = Column(String(30), nullable=False)  # CNPJ/CPF
    nome_razao_social = Column(String(255), nullable=False)
    
    # Company information
    porte_empresa_id = Column(Integer, nullable=True)
    porte_empresa_nome = Column(String(50), nullable=True)
    
    # Participation details
    situacao_fornecedor = Column(String(50), nullable=True)  # Habilitado, Desabilitado
    data_habilitacao = Column(Date, nullable=True)
    data_desabilitacao = Column(Date, nullable=True)
    motivo_desabilitacao = Column(Text, nullable=True)
    
    # Contact information
    endereco = Column(Text, nullable=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<FornecedorAtaRegistroPreco(ata_id={self.ata_id}, ni={self.ni_fornecedor})>"


class AdesaoAtaRegistroPreco(BaseModel, AuditLogModel):
    """Model for adhesions to Price Registration Records."""
    
    __tablename__ = "adesao_ata_registro_preco"
    
    # Relationship
    ata_id = Column(Integer, ForeignKey("ata_registro_preco.id"), nullable=False)
    ata = relationship("AtaRegistroPreco")
    
    # Adhesion identification
    numero_adesao = Column(String(50), nullable=False)
    tipo_adesao = Column(String(50), nullable=True)  # Carona, Registro
    
    # Adhering organization
    cnpj_orgao_aderente = Column(String(14), nullable=False)
    nome_orgao_aderente = Column(String(255), nullable=False)
    codigo_unidade_aderente = Column(String(20), nullable=True)
    nome_unidade_aderente = Column(String(255), nullable=True)
    
    # Dates
    data_adesao = Column(Date, nullable=True)
    data_vigencia_inicio = Column(Date, nullable=True)
    data_vigencia_fim = Column(Date, nullable=True)
    
    # Values
    valor_estimado_adesao = Column(Numeric(15, 4), nullable=True)
    valor_utilizado = Column(Numeric(15, 4), nullable=True)
    
    # Status
    situacao_adesao = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<AdesaoAtaRegistroPreco(ata_id={self.ata_id}, numero_adesao={self.numero_adesao})>"
