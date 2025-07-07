from enum import Enum
from typing import Dict, List

# Modalidades de Contratação conforme Lei 14.133/2021
class ModalidadeContratacao(Enum):
    CONCORRENCIA = 1
    TOMADA_PRECOS = 2
    CONVITE = 3
    CONCURSO = 4
    LEILAO = 5
    PREGAO_ELETRONICO = 6
    PREGAO_PRESENCIAL = 7
    DISPENSA_LICITACAO = 8
    INEXIGIBILIDADE = 9
    DIALOGO_COMPETITIVO = 10
    MANIFESTACAO_INTERESSE = 11
    CREDENCIAMENTO = 12
    PRE_QUALIFICACAO = 13
    CONCURSO_PROJETO = 14
    LICITACAO_INTEGRADA = 15
    LICITACAO_CONCESSAO = 16
    COMPRAS_GOVERNAMENTAIS = 17


# Modo de Disputa
class ModoDisputa(Enum):
    ABERTO = 1
    FECHADO = 2
    COMBINADO = 3


# Critério de Julgamento
class CriterioJulgamento(Enum):
    MENOR_PRECO = 1
    MELHOR_TECNICA = 2
    TECNICA_PRECO = 3
    MELHOR_CONTEUDO_ARTISTICO = 4
    MAIOR_LANCE = 5
    MAIOR_DESCONTO = 6
    MELHOR_DESTINACAO = 7


# Situação da Contratação
class SituacaoContratacao(Enum):
    PLANEJAMENTO = 1
    PUBLICADA = 2
    ABERTA = 3
    EM_ANALISE = 4
    HOMOLOGADA = 5
    ADJUDICADA = 6
    CANCELADA = 7
    REVOGADA = 8
    ANULADA = 9
    FRACASSADA = 10
    DESERTA = 11
    SUSPENSA = 12
    PRORROGADA = 13
    REABERTURA = 14
    REPUBLICADA = 15


# Situação do Item
class SituacaoItem(Enum):
    ATIVO = 1
    CANCELADO = 2
    SUSPENSO = 3
    ADJUDICADO = 4
    HOMOLOGADO = 5
    FRACASSADO = 6
    DESERTO = 7


# Tipo de Benefício
class TipoBeneficio(Enum):
    NENHUM = 1
    ME_EPP = 2
    COOPERATIVA = 3
    PRODUTOR_RURAL = 4
    ARTESAO = 5
    ORGANIZACAO_SOCIAL = 6


# Tipo de Contrato
class TipoContrato(Enum):
    COMPRA = 1
    SERVICO = 2
    OBRA = 3
    SERVICO_ENGENHARIA = 4
    CONCESSAO = 5
    PERMISSAO = 6
    ALIENACAO = 7
    LOCACAO = 8
    FORNECIMENTO = 9
    PRESTACAO_SERVICO = 10


# Porte da Empresa
class PorteEmpresa(Enum):
    MICRO_EMPRESA = 1
    PEQUENA_EMPRESA = 2
    MEDIA_EMPRESA = 3
    GRANDE_EMPRESA = 4
    COOPERATIVA = 5
    ORGANIZACAO_SOCIAL = 6


# Categoria do Processo
class CategoriaProcesso(Enum):
    LICITACAO = 1
    CONTRATACAO_DIRETA = 2
    PREGAO = 3
    REGISTRO_PRECOS = 4
    ACORDO_QUADRO = 5


# Categoria do Item PCA
class CategoriaItemPCA(Enum):
    BEM = 1
    SERVICO = 2
    OBRA = 3
    SERVICO_ENGENHARIA = 4


# Instrumento Convocatório
class InstrumentoConvocatorio(Enum):
    EDITAL = 1
    CARTA_CONVITE = 2
    AVISO = 3
    CHAMAMENTO_PUBLICO = 4


# Natureza Jurídica
class NaturezaJuridica(Enum):
    ADMINISTRACAO_PUBLICA = 1
    EMPRESA_PRIVADA = 2
    ENTIDADE_EMPRESARIAL = 3
    PESSOA_FISICA = 4
    ORGANIZACAO_SOCIAL = 5


# Amparo Legal
class AmparoLegal(Enum):
    ART_24_II = 1
    ART_24_IV = 2
    ART_24_V = 3
    ART_24_VIII = 4
    ART_24_X = 5
    ART_25_I = 6
    ART_25_II = 7
    ART_25_III = 8
    ART_75 = 9
    ART_76 = 10


# Mapeamentos para nomes legíveis
MODALIDADE_NAMES = {
    1: "Concorrência",
    2: "Tomada de Preços",
    3: "Convite",
    4: "Concurso",
    5: "Leilão",
    6: "Pregão Eletrônico",
    7: "Pregão Presencial",
    8: "Dispensa de Licitação",
    9: "Inexigibilidade de Licitação",
    10: "Diálogo Competitivo",
    11: "Procedimento de Manifestação de Interesse",
    12: "Credenciamento",
    13: "Pré-qualificação",
    14: "Concurso de Projeto",
    15: "Licitação para Contratação Integrada",
    16: "Licitação para Concessão",
    17: "Compras Governamentais"
}

SITUACAO_CONTRATACAO_NAMES = {
    1: "Planejamento",
    2: "Publicada",
    3: "Aberta",
    4: "Em Análise",
    5: "Homologada",
    6: "Adjudicada",
    7: "Cancelada",
    8: "Revogada",
    9: "Anulada",
    10: "Fracassada",
    11: "Deserta",
    12: "Suspensa",
    13: "Prorrogada",
    14: "Reabertura",
    15: "Republicada"
}

TIPO_CONTRATO_NAMES = {
    1: "Compra",
    2: "Serviço",
    3: "Obra",
    4: "Serviço de Engenharia",
    5: "Concessão",
    6: "Permissão",
    7: "Alienação",
    8: "Locação",
    9: "Fornecimento",
    10: "Prestação de Serviço"
}

PORTE_EMPRESA_NAMES = {
    1: "Micro Empresa",
    2: "Pequena Empresa",
    3: "Média Empresa",
    4: "Grande Empresa",
    5: "Cooperativa",
    6: "Organização Social"
}

AMPARO_LEGAL_NAMES = {
    1: "Art. 24, II - Guerra ou grave perturbação da ordem",
    2: "Art. 24, IV - Emergência ou calamidade pública",
    3: "Art. 24, V - Não acudiram interessados",
    4: "Art. 24, VIII - Segurança nacional",
    5: "Art. 24, X - Compra ou locação de imóvel",
    6: "Art. 25, I - Exclusividade de fornecimento",
    7: "Art. 25, II - Serviços técnicos profissionais",
    8: "Art. 25, III - Contratação de pessoa jurídica",
    9: "Art. 75 - Acordo-quadro",
    10: "Art. 76 - Ata de registro de preços"
}

# Estados brasileiros
ESTADOS_BRASIL = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins"
}

# Poderes
PODERES = {
    "E": "Executivo",
    "L": "Legislativo",
    "J": "Judiciário",
    "M": "Ministério Público",
    "T": "Tribunal de Contas"
}

# Esferas
ESFERAS = {
    "F": "Federal",
    "E": "Estadual",
    "M": "Municipal",
    "D": "Distrital"
}

# Tipos de Pessoa
TIPOS_PESSOA = {
    "PF": "Pessoa Física",
    "PJ": "Pessoa Jurídica"
}

# Configurações de paginação
PAGINATION_DEFAULTS = {
    "page_size": 50,
    "max_page_size": 500,
    "min_page_size": 1
}

# Configurações de cache
CACHE_KEYS = {
    "modalidades": "domain:modalidades_contratacao",
    "situacoes": "domain:situacoes_contratacao",
    "tipos_contrato": "domain:tipos_contrato",
    "amparos_legais": "domain:amparos_legais",
    "portes_empresa": "domain:portes_empresa"
}

# Configurações de logs
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

LOG_CATEGORIES = {
    "AUTH": "Autenticação",
    "API": "API",
    "SYNC": "Sincronização",
    "SYSTEM": "Sistema",
    "WEBHOOK": "Webhook",
    "CACHE": "Cache",
    "DATABASE": "Banco de Dados"
}

# Configurações de rate limiting
RATE_LIMITS = {
    "api_calls_per_minute": 100,
    "api_calls_per_hour": 1000,
    "webhook_calls_per_minute": 10,
    "sync_calls_per_minute": 5
}

# Configurações de timeout
TIMEOUTS = {
    "pncp_api": 30,
    "database": 10,
    "cache": 5,
    "webhook": 30
}

# Configurações de retry
RETRY_CONFIGS = {
    "max_retries": 3,
    "backoff_factor": 2,
    "retry_statuses": [500, 502, 503, 504]
}

# Validações
VALIDATION_RULES = {
    "cnpj_length": 14,
    "cpf_length": 11,
    "max_string_length": 255,
    "max_text_length": 65535,
    "max_decimal_places": 4,
    "max_decimal_digits": 15
}

# Formatos de data
DATE_FORMATS = {
    "pncp_date": "%Y%m%d",
    "iso_date": "%Y-%m-%d",
    "iso_datetime": "%Y-%m-%dT%H:%M:%S",
    "display_date": "%d/%m/%Y",
    "display_datetime": "%d/%m/%Y %H:%M:%S"
}

# URLs da API PNCP
PNCP_ENDPOINTS = {
    "base_url": "https://pncp.gov.br/api/consulta",
    "pca_usuario": "/v1/pca/usuarios/{id_usuario}",
    "pca_classificacao": "/v1/pca/classificacao-superior",
    "contratacao_publicacao": "/v1/contratacoes/publicacao",
    "contratacao_proposta": "/v1/contratacoes/proposta-aberta",
    "ata_vigencia": "/v1/atas/vigencia",
    "contrato_publicacao": "/v1/contratos/publicacao"
}

# Configurações de sincronização
SYNC_SETTINGS = {
    "batch_size": 100,
    "max_sync_attempts": 5,
    "sync_interval_minutes": 30,
    "daily_sync_hour": 6,
    "cleanup_logs_days": 30
}
