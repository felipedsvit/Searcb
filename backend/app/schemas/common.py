from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union, Generic, TypeVar

T = TypeVar('T')
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from ..utils.validators import (
    validate_cnpj, validate_cpf, validate_email, validate_uf,
    validate_modalidade_id, validate_situacao_id, validate_pagination_params
)





class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    
    pagina: int = Field(1, ge=1, description="Número da página")
    tamanho_pagina: int = Field(50, ge=1, le=500, description="Tamanho da página")
    
    @validator('pagina', 'tamanho_pagina')
    def validate_pagination(cls, v, values):
        if 'tamanho_pagina' in values:
            if not validate_pagination_params(values.get('pagina', 1), v, 500):
                raise ValueError('Parâmetros de paginação inválidos')
        return v


class PaginatedResponse(BaseModel, Generic[T]):
    """Schema for paginated responses."""
    
    data: List[T]
    total_registros: int = Field(description="Total de registros")
    total_paginas: int = Field(description="Total de páginas")
    numero_pagina: int = Field(description="Número da página atual")
    tamanho_pagina: int = Field(description="Tamanho da página")
    paginas_restantes: int = Field(description="Páginas restantes")
    empty: bool = Field(description="Indica se o resultado está vazio")
    first: bool = Field(description="Indica se é a primeira página")
    last: bool = Field(description="Indica se é a última página")
    has_next: bool = Field(description="Indica se há próxima página")
    has_previous: bool = Field(description="Indica se há página anterior")


class DateRangeFilter(BaseModel):
    """Schema for date range filtering."""
    
    data_inicio: date = Field(description="Data de início")
    data_fim: date = Field(description="Data de fim")
    
    @validator('data_fim')
    def validate_date_range(cls, v, values):
        if 'data_inicio' in values and v < values['data_inicio']:
            raise ValueError('Data de fim deve ser maior que data de início')
        return v


class OrgaoEntidade(BaseModel):
    """Schema for organization/entity information."""
    
    cnpj: str = Field(max_length=14, description="CNPJ do órgão/entidade")
    razao_social: str = Field(max_length=255, description="Razão social")
    poder_id: Optional[str] = Field(None, max_length=1, description="ID do poder")
    esfera_id: Optional[str] = Field(None, max_length=1, description="ID da esfera")
    natureza_juridica_id: Optional[int] = Field(None, description="ID da natureza jurídica")
    
    @validator('cnpj')
    def validate_cnpj_field(cls, v):
        if v and not validate_cnpj(v):
            raise ValueError('CNPJ inválido')
        return v


class UnidadeOrgao(BaseModel):
    """Schema for organization unit information."""
    
    codigo: Optional[str] = Field(None, max_length=20, description="Código da unidade")
    nome: Optional[str] = Field(None, max_length=255, description="Nome da unidade")
    codigo_ibge: Optional[int] = Field(None, description="Código IBGE")
    municipio: Optional[str] = Field(None, max_length=100, description="Município")
    uf_sigla: Optional[str] = Field(None, max_length=2, description="Sigla da UF")
    uf_nome: Optional[str] = Field(None, max_length=50, description="Nome da UF")
    
    @validator('uf_sigla')
    def validate_uf_field(cls, v):
        if v and not validate_uf(v):
            raise ValueError('UF inválida')
        return v


class AmparoLegal(BaseModel):
    """Schema for legal basis information."""
    
    codigo: Optional[int] = Field(None, description="Código do amparo legal")
    nome: Optional[str] = Field(None, max_length=255, description="Nome do amparo legal")
    descricao: Optional[str] = Field(None, description="Descrição do amparo legal")


class Fornecedor(BaseModel):
    """Schema for supplier information."""
    
    tipo_pessoa: str = Field(max_length=2, description="Tipo de pessoa (PF/PJ)")
    ni: str = Field(max_length=30, description="Número de identificação (CPF/CNPJ)")
    nome_razao_social: str = Field(max_length=255, description="Nome ou razão social")
    porte_empresa_id: Optional[int] = Field(None, description="ID do porte da empresa")
    porte_empresa_nome: Optional[str] = Field(None, max_length=50, description="Nome do porte")
    
    @validator('ni')
    def validate_ni_field(cls, v, values):
        tipo_pessoa = values.get('tipo_pessoa')
        if tipo_pessoa == 'PF' and not validate_cpf(v):
            raise ValueError('CPF inválido')
        elif tipo_pessoa == 'PJ' and not validate_cnpj(v):
            raise ValueError('CNPJ inválido')
        return v


class SearchFilters(BaseModel):
    """Schema for search filters."""
    
    query: Optional[str] = Field(None, description="Termo de busca")
    modalidade_id: Optional[int] = Field(None, description="ID da modalidade")
    situacao_id: Optional[int] = Field(None, description="ID da situação")
    uf: Optional[str] = Field(None, max_length=2, description="UF")
    cnpj: Optional[str] = Field(None, max_length=14, description="CNPJ")
    data_inicio: Optional[date] = Field(None, description="Data de início")
    data_fim: Optional[date] = Field(None, description="Data de fim")
    
    @validator('modalidade_id')
    def validate_modalidade_id_field(cls, v):
        if v and not validate_modalidade_id(v):
            raise ValueError('Modalidade ID inválida')
        return v
    
    @validator('situacao_id')
    def validate_situacao_id_field(cls, v):
        if v and not validate_situacao_id(v):
            raise ValueError('Situação ID inválida')
        return v
    
    @validator('uf')
    def validate_uf_field(cls, v):
        if v and not validate_uf(v):
            raise ValueError('UF inválida')
        return v
    
    @validator('cnpj')
    def validate_cnpj_field(cls, v):
        if v and not validate_cnpj(v):
            raise ValueError('CNPJ inválido')
        return v


class ResponseBase(BaseModel):
    """Base schema for API responses."""
    
    success: bool = Field(description="Indica se a operação foi bem-sucedida")
    message: str = Field(description="Mensagem de resposta")
    timestamp: datetime = Field(description="Timestamp da resposta")
    error_code: Optional[str] = Field(None, description="Código de erro")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")


class SuccessResponse(ResponseBase):
    """Schema for success responses."""
    
    data: Optional[Any] = Field(None, description="Dados da resposta")


class ErrorResponse(ResponseBase):
    """Schema for error responses."""
    
    success: bool = Field(default=False, description="Sempre False para erros")
    details: Optional[List[str]] = Field(None, description="Detalhes do erro")


class HealthResponse(BaseModel):
    """Schema for health check responses."""
    
    status: str = Field(description="Status do serviço")
    timestamp: datetime = Field(description="Timestamp da verificação")
    version: str = Field(description="Versão da API")
    components: Dict[str, Dict[str, Any]] = Field(description="Status dos componentes")


class MetricsResponse(BaseModel):
    """Schema for metrics responses."""
    
    api_calls_total: int = Field(description="Total de chamadas à API")
    api_calls_success: int = Field(description="Chamadas bem-sucedidas")
    api_calls_error: int = Field(description="Chamadas com erro")
    average_response_time: float = Field(description="Tempo médio de resposta")
    sync_operations_total: int = Field(description="Total de operações de sincronização")
    sync_operations_success: int = Field(description="Sincronizações bem-sucedidas")
    sync_operations_failed: int = Field(description="Sincronizações falhadas")
    cache_hits: int = Field(description="Acertos de cache")
    cache_misses: int = Field(description="Erros de cache")
    database_connections: int = Field(description="Conexões com banco de dados")


class ConfigurationItem(BaseModel):
    """Schema for configuration items."""
    
    key: str = Field(description="Chave da configuração")
    value: Optional[str] = Field(None, description="Valor da configuração")
    type: str = Field(description="Tipo da configuração")
    description: Optional[str] = Field(None, description="Descrição")
    category: Optional[str] = Field(None, description="Categoria")
    read_only: bool = Field(default=False, description="Somente leitura")


class LogEntry(BaseModel):
    """Schema for log entries."""
    
    id: int = Field(description="ID do log")
    level: str = Field(description="Nível do log")
    category: str = Field(description="Categoria do log")
    message: str = Field(description="Mensagem do log")
    timestamp: datetime = Field(description="Timestamp do log")
    user_id: Optional[int] = Field(None, description="ID do usuário")
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    endpoint: Optional[str] = Field(None, description="Endpoint da API")
    method: Optional[str] = Field(None, description="Método HTTP")
    status_code: Optional[int] = Field(None, description="Código de status")
    response_time: Optional[int] = Field(None, description="Tempo de resposta")


class BulkOperation(BaseModel):
    """Schema for bulk operations."""
    
    operation: str = Field(description="Tipo de operação")
    items: List[Dict[str, Any]] = Field(description="Itens da operação")
    options: Optional[Dict[str, Any]] = Field(None, description="Opções da operação")


class BulkOperationResult(BaseModel):
    """Schema for bulk operation results."""
    
    total_items: int = Field(description="Total de itens")
    successful_items: int = Field(description="Itens processados com sucesso")
    failed_items: int = Field(description="Itens que falharam")
    errors: List[Dict[str, Any]] = Field(description="Lista de erros")
    execution_time: float = Field(description="Tempo de execução")


class ExportRequest(BaseModel):
    """Schema for export requests."""
    
    format: str = Field(description="Formato de exportação (CSV, XLSX, JSON)")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros de exportação")
    fields: Optional[List[str]] = Field(None, description="Campos a exportar")
    
    @validator('format')
    def validate_format(cls, v):
        allowed_formats = ['CSV', 'XLSX', 'JSON']
        if v.upper() not in allowed_formats:
            raise ValueError(f'Formato deve ser um de: {", ".join(allowed_formats)}')
        return v.upper()


class ExportResponse(BaseModel):
    """Schema for export responses."""
    
    file_id: str = Field(description="ID do arquivo exportado")
    filename: str = Field(description="Nome do arquivo")
    format: str = Field(description="Formato do arquivo")
    size: int = Field(description="Tamanho do arquivo em bytes")
    records_count: int = Field(description="Número de registros")
    created_at: datetime = Field(description="Data de criação")
    download_url: str = Field(description="URL para download")
    expires_at: datetime = Field(description="Data de expiração")


class SystemInfo(BaseModel):
    """Schema for system information."""
    
    name: str = Field(description="Nome do sistema")
    version: str = Field(description="Versão do sistema")
    description: str = Field(description="Descrição do sistema")
    environment: str = Field(description="Ambiente (dev, prod, etc.)")
    uptime: str = Field(description="Tempo de atividade")
    memory_usage: float = Field(description="Uso de memória")
    cpu_usage: float = Field(description="Uso de CPU")
    disk_usage: float = Field(description="Uso de disco")
    database_status: str = Field(description="Status do banco de dados")
    cache_status: str = Field(description="Status do cache")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Sistema PNCP",
                "version": "1.0.0",
                "description": "Sistema de Gestão Pública integrado ao PNCP",
                "environment": "production",
                "uptime": "2 days, 14:30:25",
                "memory_usage": 75.5,
                "cpu_usage": 12.3,
                "disk_usage": 45.2,
                "database_status": "healthy",
                "cache_status": "healthy"
            }
        }
