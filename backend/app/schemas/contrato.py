"""
Schemas para Contratos
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from decimal import Decimal

from .common import PaginatedResponse, SuccessResponse


class ContratoItemBase(BaseModel):
    """Schema base para item do contrato"""
    sequencial_item: int = Field(..., description="Sequencial do item")
    codigo_item: str = Field(..., max_length=50, description="Código do item")
    descricao_item: str = Field(..., max_length=1000, description="Descrição do item")
    catmat_codigo: Optional[str] = Field(None, max_length=20, description="Código CATMAT")
    catmat_descricao: Optional[str] = Field(None, max_length=500, description="Descrição CATMAT")
    unidade_medida: str = Field(..., max_length=10, description="Unidade de medida")
    quantidade_contratada: Decimal = Field(..., gt=0, description="Quantidade contratada")
    valor_unitario: Decimal = Field(..., gt=0, description="Valor unitário")
    valor_total: Decimal = Field(..., gt=0, description="Valor total")
    
    @validator('valor_total')
    def validate_valor_total(cls, v, values):
        """Valida se o valor total está correto"""
        if 'quantidade_contratada' in values and 'valor_unitario' in values:
            calculated = values['quantidade_contratada'] * values['valor_unitario']
            if abs(calculated - v) > Decimal('0.01'):
                raise ValueError('Valor total não confere com quantidade x valor unitário')
        return v


class ContratoItemCreate(ContratoItemBase):
    """Schema para criação de item do contrato"""
    pass


class ContratoItemUpdate(BaseModel):
    """Schema para atualização de item do contrato"""
    descricao_item: Optional[str] = Field(None, max_length=1000)
    catmat_codigo: Optional[str] = Field(None, max_length=20)
    catmat_descricao: Optional[str] = Field(None, max_length=500)
    unidade_medida: Optional[str] = Field(None, max_length=10)
    quantidade_contratada: Optional[Decimal] = Field(None, gt=0)
    valor_unitario: Optional[Decimal] = Field(None, gt=0)
    valor_total: Optional[Decimal] = Field(None, gt=0)


class ContratoItemResponse(ContratoItemBase):
    """Schema para resposta de item do contrato"""
    id: int
    contrato_id: int
    criado_em: datetime
    atualizado_em: datetime
    
    class Config:
        from_attributes = True


class ContratoBase(BaseModel):
    """Schema base para contrato"""
    numero_contrato: str = Field(..., max_length=100, description="Número do contrato")
    numero_processo: str = Field(..., max_length=100, description="Número do processo")
    orgao_cnpj: str = Field(..., max_length=14, description="CNPJ do órgão")
    orgao_nome: str = Field(..., max_length=200, description="Nome do órgão")
    orgao_poder: str = Field(..., max_length=50, description="Poder do órgão")
    orgao_esfera: str = Field(..., max_length=50, description="Esfera do órgão")
    unidade_nome: Optional[str] = Field(None, max_length=200, description="Nome da unidade")
    unidade_codigo: Optional[str] = Field(None, max_length=20, description="Código da unidade")
    modalidade_nome: str = Field(..., max_length=100, description="Modalidade de contratação")
    modalidade_codigo: str = Field(..., max_length=10, description="Código da modalidade")
    situacao: str = Field(..., max_length=50, description="Situação do contrato")
    objeto_contrato: str = Field(..., max_length=2000, description="Objeto do contrato")
    valor_inicial: Decimal = Field(..., gt=0, description="Valor inicial do contrato")
    valor_atual: Decimal = Field(..., gt=0, description="Valor atual do contrato")
    data_assinatura: Optional[datetime] = Field(None, description="Data de assinatura")
    data_inicio_vigencia: Optional[datetime] = Field(None, description="Data de início da vigência")
    data_fim_vigencia: Optional[datetime] = Field(None, description="Data de fim da vigência")
    data_publicacao: Optional[datetime] = Field(None, description="Data de publicação")
    fornecedor_nome: str = Field(..., max_length=200, description="Nome do fornecedor")
    fornecedor_cnpj_cpf: str = Field(..., max_length=14, description="CNPJ/CPF do fornecedor")
    
    @validator('orgao_cnpj')
    def validate_cnpj(cls, v):
        """Valida CNPJ"""
        from ..utils.validators import validate_cnpj
        if not validate_cnpj(v):
            raise ValueError('CNPJ inválido')
        return v
    
    @validator('fornecedor_cnpj_cpf')
    def validate_fornecedor_documento(cls, v):
        """Valida documento do fornecedor"""
        from ..utils.validators import validate_cnpj, validate_cpf
        if len(v) == 14:
            if not validate_cnpj(v):
                raise ValueError('CNPJ do fornecedor inválido')
        elif len(v) == 11:
            if not validate_cpf(v):
                raise ValueError('CPF do fornecedor inválido')
        else:
            raise ValueError('Documento do fornecedor deve ser CPF ou CNPJ')
        return v


class ContratoCreate(ContratoBase):
    """Schema para criação de contrato"""
    itens: List[ContratoItemCreate] = Field(..., min_items=1, description="Lista de itens do contrato")


class ContratoUpdate(BaseModel):
    """Schema para atualização de contrato"""
    orgao_nome: Optional[str] = Field(None, max_length=200)
    orgao_poder: Optional[str] = Field(None, max_length=50)
    orgao_esfera: Optional[str] = Field(None, max_length=50)
    unidade_nome: Optional[str] = Field(None, max_length=200)
    unidade_codigo: Optional[str] = Field(None, max_length=20)
    modalidade_nome: Optional[str] = Field(None, max_length=100)
    modalidade_codigo: Optional[str] = Field(None, max_length=10)
    situacao: Optional[str] = Field(None, max_length=50)
    objeto_contrato: Optional[str] = Field(None, max_length=2000)
    valor_inicial: Optional[Decimal] = Field(None, gt=0)
    valor_atual: Optional[Decimal] = Field(None, gt=0)
    data_assinatura: Optional[datetime] = None
    data_inicio_vigencia: Optional[datetime] = None
    data_fim_vigencia: Optional[datetime] = None
    data_publicacao: Optional[datetime] = None
    fornecedor_nome: Optional[str] = Field(None, max_length=200)
    fornecedor_cnpj_cpf: Optional[str] = Field(None, max_length=14)


class ContratoResponse(ContratoBase):
    """Schema para resposta de contrato"""
    id: int
    pncp_id: str
    criado_em: datetime
    atualizado_em: datetime
    sincronizado_em: Optional[datetime] = None
    itens: List[ContratoItemResponse] = []
    
    class Config:
        from_attributes = True


class ContratoFilter(BaseModel):
    """Schema para filtros de contrato"""
    numero_contrato: Optional[str] = Field(None, max_length=100)
    numero_processo: Optional[str] = Field(None, max_length=100)
    orgao_cnpj: Optional[str] = Field(None, max_length=14)
    orgao_nome: Optional[str] = Field(None, max_length=200)
    orgao_poder: Optional[str] = Field(None, max_length=50)
    orgao_esfera: Optional[str] = Field(None, max_length=50)
    unidade_nome: Optional[str] = Field(None, max_length=200)
    modalidade_nome: Optional[str] = Field(None, max_length=100)
    modalidade_codigo: Optional[str] = Field(None, max_length=10)
    situacao: Optional[str] = Field(None, max_length=50)
    data_assinatura_inicio: Optional[datetime] = None
    data_assinatura_fim: Optional[datetime] = None
    data_inicio_vigencia_inicio: Optional[datetime] = None
    data_inicio_vigencia_fim: Optional[datetime] = None
    data_fim_vigencia_inicio: Optional[datetime] = None
    data_fim_vigencia_fim: Optional[datetime] = None
    valor_minimo: Optional[Decimal] = Field(None, gt=0)
    valor_maximo: Optional[Decimal] = Field(None, gt=0)
    fornecedor_nome: Optional[str] = Field(None, max_length=200)
    fornecedor_cnpj_cpf: Optional[str] = Field(None, max_length=14)
    
    @validator('valor_maximo')
    def validate_valores(cls, v, values):
        """Valida se valor máximo é maior que mínimo"""
        if v and 'valor_minimo' in values and values['valor_minimo']:
            if v <= values['valor_minimo']:
                raise ValueError('Valor máximo deve ser maior que o mínimo')
        return v


class ContratoListResponse(SuccessResponse):
    """Schema para resposta de lista de contratos"""
    data: PaginatedResponse[ContratoResponse]


class ContratoDetailResponse(SuccessResponse):
    """Schema para resposta de detalhe de contrato"""
    data: ContratoResponse


class ContratoStatsResponse(SuccessResponse):
    """Schema para resposta de estatísticas de contrato"""
    data: dict = Field(..., description="Estatísticas do contrato")


class ContratoExportRequest(BaseModel):
    """Schema para requisição de exportação de contrato"""
    formato: str = Field(..., pattern="^(csv|excel|pdf)$", description="Formato de exportação")
    filtros: Optional[ContratoFilter] = None
    incluir_itens: bool = Field(True, description="Incluir itens na exportação")
