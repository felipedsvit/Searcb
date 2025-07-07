from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from .base import BaseModel, AuditLogModel, SyncLogModel


class PCA(BaseModel, AuditLogModel, SyncLogModel):
    """Model for Plano de Contratações Anual (PCA)."""
    
    __tablename__ = "pca"
    
    # PNCP Identification
    id_pca_pncp = Column(String(50), unique=True, index=True, nullable=False)
    ano_pca = Column(Integer, index=True, nullable=False)
    data_publicacao_pncp = Column(Date, nullable=True)
    
    # Organization/Entity
    orgao_entidade_cnpj = Column(String(14), index=True, nullable=False)
    orgao_entidade_razao_social = Column(String(255), nullable=False)
    codigo_unidade = Column(String(20), nullable=True)
    nome_unidade = Column(String(255), nullable=True)
    
    # Additional fields
    numero_pca = Column(String(50), nullable=True)
    situacao_pca = Column(String(50), nullable=True)
    data_inicio_vigencia = Column(Date, nullable=True)
    data_fim_vigencia = Column(Date, nullable=True)
    
    # System fields
    usuario_nome = Column(String(255), nullable=True)
    sistema_origem = Column(String(100), nullable=True)
    
    # Relationships
    itens = relationship("ItemPCA", back_populates="pca", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PCA(id_pca_pncp={self.id_pca_pncp}, ano={self.ano_pca})>"


class ItemPCA(BaseModel, AuditLogModel):
    """Model for PCA items."""
    
    __tablename__ = "item_pca"
    
    # Relationship with PCA
    pca_id = Column(Integer, ForeignKey("pca.id"), nullable=False)
    pca = relationship("PCA", back_populates="itens")
    
    # Item identification
    numero_item = Column(Integer, nullable=False)
    categoria_item_pca_id = Column(Integer, nullable=True)
    categoria_item_pca_nome = Column(String(100), nullable=True)
    
    # Classification
    classificacao_catalogo_id = Column(String(10), nullable=True)
    nome_classificacao_catalogo = Column(String(50), nullable=True)
    classificacao_superior_codigo = Column(String(100), index=True, nullable=True)
    classificacao_superior_nome = Column(String(255), nullable=True)
    
    # PDM (Plano de Desenvolvimento de Mercado)
    pdm_codigo = Column(String(100), nullable=True)
    pdm_descricao = Column(String(255), nullable=True)
    
    # Item description
    codigo_item = Column(String(100), nullable=True)
    descricao_item = Column(Text, nullable=False)
    unidade_fornecimento = Column(String(20), nullable=True)
    especificacao_tecnica = Column(Text, nullable=True)
    
    # Quantities and values
    quantidade_estimada = Column(Numeric(15, 4), nullable=True)
    valor_unitario = Column(Numeric(15, 4), nullable=True)
    valor_total = Column(Numeric(15, 4), nullable=True)
    valor_orcamento_exercicio = Column(Numeric(15, 4), nullable=True)
    
    # Dates and additional info
    data_desejada = Column(Date, nullable=True)
    unidade_requisitante = Column(String(255), nullable=True)
    grupo_contratacao_codigo = Column(String(50), nullable=True)
    grupo_contratacao_nome = Column(String(255), nullable=True)
    data_inclusao = Column(Date, nullable=True)
    data_atualizacao = Column(Date, nullable=True)
    
    # Contracting information
    modalidade_contratacao_id = Column(Integer, nullable=True)
    modalidade_contratacao_nome = Column(String(100), nullable=True)
    criterio_julgamento_id = Column(Integer, nullable=True)
    criterio_julgamento_nome = Column(String(100), nullable=True)
    
    # Status
    situacao_item = Column(String(50), nullable=True)
    observacoes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ItemPCA(pca_id={self.pca_id}, numero_item={self.numero_item})>"


class HistoricoPCA(BaseModel):
    """Model for PCA history tracking."""
    
    __tablename__ = "historico_pca"
    
    # Reference to PCA
    pca_id = Column(Integer, ForeignKey("pca.id"), nullable=False)
    pca = relationship("PCA")
    
    # Change tracking
    campo_alterado = Column(String(100), nullable=False)
    valor_anterior = Column(Text, nullable=True)
    valor_novo = Column(Text, nullable=True)
    tipo_operacao = Column(String(20), nullable=False)  # INSERT, UPDATE, DELETE
    
    # User info
    usuario_alteracao = Column(String(255), nullable=True)
    motivo_alteracao = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<HistoricoPCA(pca_id={self.pca_id}, campo={self.campo_alterado})>"
