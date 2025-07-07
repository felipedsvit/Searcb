"""
Schemas para administração do sistema
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class LogSistemaResponse(BaseModel):
    """Schema para resposta de log do sistema"""
    id: int
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
    usuario_id: Optional[int] = None
    timestamp: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConfiguracaoSistemaResponse(BaseModel):
    """Schema para resposta de configuração do sistema"""
    id: int
    chave: str
    valor: Optional[str] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    tipo: str
    ativo: bool
    somente_leitura: bool
    valor_padrao: Optional[str] = None
    valor_minimo: Optional[str] = None
    valor_maximo: Optional[str] = None
    ultima_atualizacao: datetime
    
    class Config:
        from_attributes = True


class AtualizarConfiguracaoRequest(BaseModel):
    """Schema para atualização de configuração"""
    valor: str = Field(..., description="Novo valor da configuração")


class NotificacaoInternaRequest(BaseModel):
    """Schema para notificação interna"""
    tipo: str = Field(..., description="Tipo de notificação")
    dados: Dict[str, Any] = Field(..., description="Dados da notificação")
    origem: str = Field("sistema", description="Sistema/módulo de origem")
    prioridade: str = Field("normal", description="Prioridade da notificação")
    
    class Config:
        schema_extra = {
            "example": {
                "tipo": "contrato_vencendo",
                "dados": {
                    "contrato_id": 123,
                    "numero_contrato": "CT-2024-001",
                    "dias_vencimento": 30
                },
                "origem": "sistema_monitoramento",
                "prioridade": "alta"
            }
        }


class NotificacaoInternaResponse(BaseModel):
    """Schema para resposta de notificação interna"""
    status: str
    message: str
    tipo: str
    timestamp: str


class DashboardResponse(BaseModel):
    """Schema para resposta do dashboard"""
    total_usuarios: int
    total_pcas: int
    total_contratacoes: int
    total_atas: int
    total_contratos: int
    sincronizacoes_hoje: int
    ultimas_sincronizacoes: List[Dict[str, Any]]
    alertas_sistema: List[Dict[str, Any]]
    
    class Config:
        schema_extra = {
            "example": {
                "total_usuarios": 150,
                "total_pcas": 1200,
                "total_contratacoes": 5400,
                "total_atas": 800,
                "total_contratos": 2100,
                "sincronizacoes_hoje": 45,
                "ultimas_sincronizacoes": [
                    {
                        "tipo": "contratacoes",
                        "timestamp": "2024-01-15T10:30:00",
                        "status": "sucesso",
                        "registros": 25
                    }
                ],
                "alertas_sistema": [
                    {
                        "tipo": "contrato_vencendo",
                        "mensagem": "5 contratos vencem nos próximos 30 dias",
                        "prioridade": "media"
                    }
                ]
            }
        }
