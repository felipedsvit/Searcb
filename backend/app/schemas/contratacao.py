"""
Schemas para Contratações
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

from .common import PaginatedResponse, SuccessResponse, ErrorResponse


class ContratacaoItemBase(BaseModel):
    """Schema base para item da contratação"""
    sequencial_item: int = Field(..., description="Sequencial do item")
    codigo_item: str = Field(..., max_length=50, description="Código do item")
    descricao_item: str = Field(..., max_length=1000, description="Descrição do item")
    catmat_codigo: Optional[str] = Field(None, max_length=20, description="Código CATMAT")
    catmat_descricao: Optional[str] = Field(None, max_length=500, description="Descrição CATMAT")
    unidade_medida: str = Field(..., max_length=10, description="Unidade de medida")
    quantidade: Decimal = Field(..., gt=0, description="Quantidade")
    valor_unitario: Decimal = Field(..., gt=0, description="Valor unitário")
    valor_total: Decimal = Field(..., gt=0, description="Valor total")
    
    @field_validator('valor_total')
    @classmethod
    def validate_valor_total(cls, v, info):
        """Valida se o valor total está correto"""
        if info.data and 'quantidade' in info.data and 'valor_unitario' in info.data:
            calculated = info.data['quantidade'] * info.data['valor_unitario']
            if abs(calculated - v) > Decimal('0.01'):
                raise ValueError('Valor total não confere com quantidade x valor unitário')
        return v


class ContratacaoItemCreate(ContratacaoItemBase):
    """Schema para criação de item da contratação"""
    pass


class ContratacaoItemUpdate(BaseModel):
    """Schema para atualização de item da contratação"""
    descricao_item: Optional[str] = Field(None, max_length=1000)
    catmat_codigo: Optional[str] = Field(None, max_length=20)
    catmat_descricao: Optional[str] = Field(None, max_length=500)
    unidade_medida: Optional[str] = Field(None, max_length=10)
    quantidade: Optional[Decimal] = Field(None, gt=0)
    valor_unitario: Optional[Decimal] = Field(None, gt=0)
    valor_total: Optional[Decimal] = Field(None, gt=0)


class ContratacaoItemResponse(ContratacaoItemBase):
    """Schema para resposta de item da contratação"""
    id: int
    contratacao_id: int
    criado_em: datetime
    atualizado_em: datetime
    
    class Config:
        from_attributes = True


class ContratacaoBase(BaseModel):
    """Schema base para contratação"""
    numero_processo: str = Field(..., max_length=100, description="Número do processo")
    orgao_cnpj: str = Field(..., max_length=14, description="CNPJ do órgão")
    orgao_nome: str = Field(..., max_length=200, description="Nome do órgão")
    orgao_poder: str = Field(..., max_length=50, description="Poder do órgão")
    orgao_esfera: str = Field(..., max_length=50, description="Esfera do órgão")
    unidade_nome: Optional[str] = Field(None, max_length=200, description="Nome da unidade")
    unidade_codigo: Optional[str] = Field(None, max_length=20, description="Código da unidade")
    modalidade_nome: str = Field(..., max_length=100, description="Modalidade de contratação")
    modalidade_codigo: str = Field(..., max_length=10, description="Código da modalidade")
    situacao: str = Field(..., max_length=50, description="Situação da contratação")
    objeto_contratacao: str = Field(..., max_length=2000, description="Objeto da contratação")
    valor_total_estimado: Decimal = Field(..., gt=0, description="Valor total estimado")
    data_abertura: Optional[datetime] = Field(None, description="Data de abertura")
    data_publicacao: Optional[datetime] = Field(None, description="Data de publicação")
    data_encerramento: Optional[datetime] = Field(None, description="Data de encerramento")
    link_edital: Optional[str] = Field(None, max_length=500, description="Link do edital")
    
    @field_validator('orgao_cnpj')
    @classmethod
    def validate_cnpj(cls, v):
        """Valida CNPJ"""
        from ..utils.validators import validate_cnpj
        if not validate_cnpj(v):
            raise ValueError('CNPJ inválido')
        return v


class ContratacaoCreate(ContratacaoBase):
    """Schema para criação de contratação"""
    itens: List[ContratacaoItemCreate] = Field(..., min_items=1, description="Lista de itens")


class ContratacaoUpdate(BaseModel):
    """Schema para atualização de contratação"""
    orgao_nome: Optional[str] = Field(None, max_length=200)
    orgao_poder: Optional[str] = Field(None, max_length=50)
    orgao_esfera: Optional[str] = Field(None, max_length=50)
    unidade_nome: Optional[str] = Field(None, max_length=200)
    unidade_codigo: Optional[str] = Field(None, max_length=20)
    modalidade_nome: Optional[str] = Field(None, max_length=100)
    modalidade_codigo: Optional[str] = Field(None, max_length=10)
    situacao: Optional[str] = Field(None, max_length=50)
    objeto_contratacao: Optional[str] = Field(None, max_length=2000)
    valor_total_estimado: Optional[Decimal] = Field(None, gt=0)
    data_abertura: Optional[datetime] = None
    data_publicacao: Optional[datetime] = None
    data_encerramento: Optional[datetime] = None
    link_edital: Optional[str] = Field(None, max_length=500)


class ContratacaoResponse(ContratacaoBase):
    """Schema para resposta de contratação"""
    id: int
    pncp_id: str
    criado_em: datetime
    atualizado_em: datetime
    sincronizado_em: Optional[datetime] = None
    itens: List[ContratacaoItemResponse] = []
    
    class Config:
        from_attributes = True


class ContratacaoFilter(BaseModel):
    """Schema para filtros de contratação"""
    numero_processo: Optional[str] = Field(None, max_length=100)
    orgao_cnpj: Optional[str] = Field(None, max_length=14)
    orgao_nome: Optional[str] = Field(None, max_length=200)
    orgao_poder: Optional[str] = Field(None, max_length=50)
    orgao_esfera: Optional[str] = Field(None, max_length=50)
    unidade_nome: Optional[str] = Field(None, max_length=200)
    modalidade_nome: Optional[str] = Field(None, max_length=100)
    modalidade_codigo: Optional[str] = Field(None, max_length=10)
    situacao: Optional[str] = Field(None, max_length=50)
    data_abertura_inicio: Optional[datetime] = None
    data_abertura_fim: Optional[datetime] = None
    data_publicacao_inicio: Optional[datetime] = None
    data_publicacao_fim: Optional[datetime] = None
    valor_minimo: Optional[Decimal] = Field(None, gt=0)
    valor_maximo: Optional[Decimal] = Field(None, gt=0)
    
    @field_validator('valor_maximo')
    @classmethod
    def validate_valores(cls, v, info):
        """Valida se valor máximo é maior que mínimo"""
        if v and info.data and 'valor_minimo' in info.data and info.data['valor_minimo']:
            if v <= info.data['valor_minimo']:
                raise ValueError('Valor máximo deve ser maior que o mínimo')
        return v


class ContratacaoListResponse(SuccessResponse):
    """Schema para resposta de lista de contratações"""
    data: PaginatedResponse[ContratacaoResponse]


class ContratacaoDetailResponse(SuccessResponse):
    """Schema para resposta de detalhe de contratação"""
    data: ContratacaoResponse


class ContratacaoStatsResponse(SuccessResponse):
    """Schema para resposta de estatísticas de contratação"""
    data: dict = Field(..., description="Estatísticas da contratação")


class ContratacaoExportRequest(BaseModel):
    """Schema para requisição de exportação de contratação"""
    formato: str = Field(..., pattern="^(csv|excel|pdf)$", description="Formato de exportação")
    filtros: Optional[ContratacaoFilter] = None
    incluir_itens: bool = Field(True, description="Incluir itens na exportação")
