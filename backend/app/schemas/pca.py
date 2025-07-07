"""
Schemas para PCA (Plano de Contratações Anuais)
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from decimal import Decimal

from .common import PaginatedResponse, SuccessResponse, SuccessResponse


class PCAItemBase(BaseModel):
    """Schema base para item do PCA"""
    sequencial_item: int = Field(..., description="Sequencial do item no PCA")
    codigo_item: str = Field(..., max_length=50, description="Código do item")
    descricao_item: str = Field(..., max_length=1000, description="Descrição do item")
    catmat_codigo: Optional[str] = Field(None, max_length=20, description="Código CATMAT")
    catmat_descricao: Optional[str] = Field(None, max_length=500, description="Descrição CATMAT")
    unidade_medida: str = Field(..., max_length=10, description="Unidade de medida")
    quantidade_estimada: Decimal = Field(..., gt=0, description="Quantidade estimada")
    valor_unitario_estimado: Decimal = Field(..., gt=0, description="Valor unitário estimado")
    valor_total_estimado: Decimal = Field(..., gt=0, description="Valor total estimado")
    mes_contratacao: int = Field(..., ge=1, le=12, description="Mês previsto para contratação")
    modalidade_contratacao: str = Field(..., max_length=100, description="Modalidade de contratação")
    situacao: str = Field(..., max_length=50, description="Situação do item")
    
    @validator('valor_total_estimado')
    def validate_valor_total(cls, v, values):
        """Valida se o valor total está correto"""
        if 'quantidade_estimada' in values and 'valor_unitario_estimado' in values:
            calculated = values['quantidade_estimada'] * values['valor_unitario_estimado']
            if abs(calculated - v) > Decimal('0.01'):
                raise ValueError('Valor total não confere com quantidade x valor unitário')
        return v


class PCAItemCreate(PCAItemBase):
    """Schema para criação de item do PCA"""
    pass


class PCAItemUpdate(BaseModel):
    """Schema para atualização de item do PCA"""
    descricao_item: Optional[str] = Field(None, max_length=1000)
    catmat_codigo: Optional[str] = Field(None, max_length=20)
    catmat_descricao: Optional[str] = Field(None, max_length=500)
    unidade_medida: Optional[str] = Field(None, max_length=10)
    quantidade_estimada: Optional[Decimal] = Field(None, gt=0)
    valor_unitario_estimado: Optional[Decimal] = Field(None, gt=0)
    valor_total_estimado: Optional[Decimal] = Field(None, gt=0)
    mes_contratacao: Optional[int] = Field(None, ge=1, le=12)
    modalidade_contratacao: Optional[str] = Field(None, max_length=100)
    situacao: Optional[str] = Field(None, max_length=50)


class PCAItemResponse(PCAItemBase):
    """Schema para resposta de item do PCA"""
    id: int
    pca_id: int
    criado_em: datetime
    atualizado_em: datetime
    
    class Config:
        from_attributes = True


class PCABase(BaseModel):
    """Schema base para PCA"""
    exercicio: int = Field(..., ge=2020, le=2030, description="Exercício do PCA")
    orgao_cnpj: str = Field(..., max_length=14, description="CNPJ do órgão")
    orgao_nome: str = Field(..., max_length=200, description="Nome do órgão")
    orgao_poder: str = Field(..., max_length=50, description="Poder do órgão")
    orgao_esfera: str = Field(..., max_length=50, description="Esfera do órgão")
    unidade_nome: Optional[str] = Field(None, max_length=200, description="Nome da unidade")
    unidade_codigo: Optional[str] = Field(None, max_length=20, description="Código da unidade")
    situacao: str = Field(..., max_length=50, description="Situação do PCA")
    data_publicacao: Optional[datetime] = Field(None, description="Data de publicação")
    valor_total_estimado: Decimal = Field(..., gt=0, description="Valor total estimado do PCA")
    
    @validator('orgao_cnpj')
    def validate_cnpj(cls, v):
        """Valida CNPJ"""
        from ..utils.validators import validate_cnpj
        if not validate_cnpj(v):
            raise ValueError('CNPJ inválido')
        return v


class PCACreate(PCABase):
    """Schema para criação de PCA"""
    itens: List[PCAItemCreate] = Field(..., min_items=1, description="Lista de itens do PCA")


class PCAUpdate(BaseModel):
    """Schema para atualização de PCA"""
    orgao_nome: Optional[str] = Field(None, max_length=200)
    orgao_poder: Optional[str] = Field(None, max_length=50)
    orgao_esfera: Optional[str] = Field(None, max_length=50)
    unidade_nome: Optional[str] = Field(None, max_length=200)
    unidade_codigo: Optional[str] = Field(None, max_length=20)
    situacao: Optional[str] = Field(None, max_length=50)
    data_publicacao: Optional[datetime] = None
    valor_total_estimado: Optional[Decimal] = Field(None, gt=0)


class PCAResponse(PCABase):
    """Schema para resposta de PCA"""
    id: int
    pncp_id: str
    criado_em: datetime
    atualizado_em: datetime
    sincronizado_em: Optional[datetime] = None
    itens: List[PCAItemResponse] = []
    
    class Config:
        from_attributes = True


class PCAFilter(BaseModel):
    """Schema para filtros de PCA"""
    exercicio: Optional[int] = Field(None, ge=2020, le=2030)
    orgao_cnpj: Optional[str] = Field(None, max_length=14)
    orgao_nome: Optional[str] = Field(None, max_length=200)
    orgao_poder: Optional[str] = Field(None, max_length=50)
    orgao_esfera: Optional[str] = Field(None, max_length=50)
    unidade_nome: Optional[str] = Field(None, max_length=200)
    situacao: Optional[str] = Field(None, max_length=50)
    data_publicacao_inicio: Optional[datetime] = None
    data_publicacao_fim: Optional[datetime] = None
    valor_minimo: Optional[Decimal] = Field(None, gt=0)
    valor_maximo: Optional[Decimal] = Field(None, gt=0)
    
    @validator('valor_maximo')
    def validate_valores(cls, v, values):
        """Valida se valor máximo é maior que mínimo"""
        if v and 'valor_minimo' in values and values['valor_minimo']:
            if v <= values['valor_minimo']:
                raise ValueError('Valor máximo deve ser maior que o mínimo')
        return v


class PCAListResponse(SuccessResponse):
    """Schema para resposta de lista de PCAs"""
    data: PaginatedResponse[PCAResponse]


class PCADetailResponse(SuccessResponse):
    """Schema para resposta de detalhe de PCA"""
    data: PCAResponse


class PCAStatsResponse(SuccessResponse):
    """Schema para resposta de estatísticas de PCA"""
    data: dict = Field(..., description="Estatísticas do PCA")


class PCAExportRequest(BaseModel):
    """Schema para requisição de exportação de PCA"""
    formato: str = Field(..., pattern="^(csv|excel|pdf)$", description="Formato de exportação")
    filtros: Optional[PCAFilter] = None
    incluir_itens: bool = Field(True, description="Incluir itens na exportação")


class PaginatedPCAResponse(PaginatedResponse[PCAResponse]):
    """Schema de resposta paginada para PCA"""
    pass
