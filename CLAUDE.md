# Sistema de Gestão Pública - Backend PNCP

## Visão Geral

Este backend implementa uma API RESTful moderna para integração e gestão de dados do Portal Nacional de Contratações Públicas (PNCP), conforme Lei nº 14.133/2021. Ele cobre Planos Anuais de Contratações (PCA), Contratações, Atas de Registro de Preços e Contratos, com autenticação JWT, paginação, cache, sincronização, validação e documentação automática.

---

## Autenticação e Autorização

- **Modelo:** JWT Bearer Token.
- **Fluxo:** O usuário faz login e recebe um token JWT. Todas as rotas protegidas exigem o header `Authorization: Bearer <token>`.
- **Perfis:** admin, gestor, consulta.
- **Endpoints:**
  - `POST /api/v1/auth/login` — Autentica usuário e retorna token.
  - `POST /api/v1/auth/refresh` — Renova o token.
  - `GET /api/v1/auth/me` — Retorna dados do usuário autenticado.

---

## Endpoints REST

### 1. Planos Anuais de Contratações (PCA)

#### a) Consultar PCA por ano e usuário

- **GET /api/v1/pca**
- **Query Params:** `ano_pca` (int, obrigatório), `id_usuario` (int, opcional), `codigo_classificacao_superior` (str, opcional), `pagina` (int, padrão 1), `tamanho_pagina` (int, padrão 50, máx 500)
- **Lógica:** Busca PCA localmente e/ou via PNCP, aplica filtros, paginação e retorna itens detalhados.
- **Exemplo:**
  ```
  GET /api/v1/pca?ano_pca=2024&id_usuario=123&pagina=1&tamanho_pagina=50
  Authorization: Bearer <token>
  ```
- **Resposta:** Lista paginada de PCAs, incluindo campos principais e itens.

#### b) Consultar PCA por classificação

- **GET /api/v1/pca/classificacao**
- **Query Params:** iguais ao endpoint anterior, exceto `id_usuario` é opcional.
- **Lógica:** Busca PCA filtrando por classificação superior.

---

### 2. Contratações

#### a) Consultar contratações por período, modalidade e filtros

- **GET /api/v1/contratacoes**
- **Query Params:** `data_inicial` (YYYY-MM-DD, obrigatório), `data_final` (YYYY-MM-DD, obrigatório), `codigo_modalidade_contratacao` (int, opcional), `codigo_modo_disputa` (int, opcional), `uf` (str, opcional), `codigo_municipio_ibge` (str, opcional), `cnpj` (str, opcional), `codigo_unidade_administrativa` (str, opcional), `id_usuario` (int, opcional), `pagina` (int, padrão 1), `tamanho_pagina` (int, padrão 50, máx 500)
- **Lógica:** Consulta banco local e/ou PNCP, aplica filtros, paginação e retorna contratações detalhadas.
- **Exemplo:**
  ```
  GET /api/v1/contratacoes?data_inicial=2024-01-01&data_final=2024-01-31&codigo_modalidade_contratacao=6
  Authorization: Bearer <token>
  ```
- **Resposta:** Lista paginada de contratações, incluindo campos como número de controle PNCP, CNPJ, modalidade, situação, objeto, datas, etc.

#### b) Consultar contratações com propostas em aberto

- **GET /api/v1/contratacoes/propostas-abertas**
- **Query Params:** semelhantes ao endpoint anterior, mas exige `data_final`.
- **Lógica:** Retorna contratações com propostas abertas no período.

---

### 3. Atas de Registro de Preços

#### a) Consultar atas por vigência

- **GET /api/v1/atas**
- **Query Params:** `data_inicial` (YYYY-MM-DD, obrigatório), `data_final` (YYYY-MM-DD, obrigatório), `id_usuario`, `cnpj`, `codigo_unidade_administrativa`, `pagina`, `tamanho_pagina` (opcionais)
- **Lógica:** Busca atas locais e/ou PNCP, filtra por vigência, pagina e retorna detalhes.

---

### 4. Contratos

#### a) Consultar contratos por publicação

- **GET /api/v1/contratos**
- **Query Params:** `data_inicial` (YYYY-MM-DD, obrigatório), `data_final` (YYYY-MM-DD, obrigatório), `cnpj_orgao`, `codigo_unidade_administrativa`, `usuario_id`, `pagina`, `tamanho_pagina` (opcionais)
- **Lógica:** Busca contratos locais e/ou PNCP, filtra por publicação, pagina e retorna detalhes.

---

### 5. Tabelas de Domínio

#### a) Modalidades de contratação

- **GET /api/v1/domain/modalidades**
- **Lógica:** Retorna dicionário `{codigo: nome}` das modalidades, com cache.

#### b) Situações de contratação

- **GET /api/v1/domain/situacoes**
- **Lógica:** Retorna dicionário `{codigo: nome}` das situações.

#### c) Usuários integrados

- **GET /api/v1/domain/usuarios**
- **Lógica:** Lista usuários/sistemas integrados ao PNCP.

---

### 6. Webhooks (Opcional, se PNCP suportar)

- **POST /api/v1/pncp-webhooks/notifications**
- **Headers:** `x-pncp-signature` (assinatura HMAC)
- **Body:** JSON com notificação.
- **Lógica:** Valida assinatura, enfileira processamento assíncrono.

---

## Lógicas Internas e Estratégias

- **Validação:** Todos os dados recebidos e enviados são validados por schemas Pydantic. Códigos de domínio são checados contra tabelas locais/cache.
- **Cache:** Redis para tabelas de domínio e resultados frequentes.
- **Sincronização:** Celery + agendamento para sincronizar dados do PNCP periodicamente.
- **Rate Limiting:** Limita requisições por usuário/IP para evitar abuso.
- **Monitoramento:** Logging estruturado (structlog), métricas Prometheus/Grafana.
- **Documentação:** Swagger/OpenAPI gerado automaticamente em `/docs`.

---

## Exemplos de Chamadas HTTP

```http
# Login
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "senha"
}

# Buscar PCA
GET /api/v1/pca?ano_pca=2024&pagina=1&tamanho_pagina=50
Authorization: Bearer <token>

# Buscar Contratações
GET /api/v1/contratacoes?data_inicial=2024-01-01&data_final=2024-01-31&codigo_modalidade_contratacao=6
Authorization: Bearer <token>

# Buscar Modalidades
GET /api/v1/domain/modalidades
Authorization: Bearer <token>
```

---

## Observações Finais

- Todos os endpoints retornam erros padronizados (400, 401, 403, 404, 422, 500) com mensagens claras.
- Os códigos das tabelas de domínio seguem o manual do PNCP e são atualizados periodicamente.
- O backend está preparado para expansão futura (webhooks, novos domínios, integrações).

---
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)

cache = CacheService()
Modelos de Dados

Modelo Base


# app/models/base.py
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
Modelo PCA


# app/models/pca.py
from sqlalchemy import Column, String, Integer, Decimal, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class PCA(BaseModel):
    __tablename__ = "pca"
    
    # Identificação
    id_pca_pncp = Column(String(50), unique=True, index=True)
    ano_pca = Column(Integer, index=True)
    data_publicacao_pncp = Column(Date)
    
    # Órgão/Entidade
    orgao_entidade_cnpj = Column(String(14), index=True)
    orgao_entidade_razao_social = Column(String(255))
    codigo_unidade = Column(String(20))
    nome_unidade = Column(String(255))
    
    # Relacionamentos
    itens = relationship("ItemPCA", back_populates="pca")

class ItemPCA(BaseModel):
    __tablename__ = "item_pca"
    
    # Relacionamento com PCA
    pca_id = Column(Integer, ForeignKey("pca.id"))
    pca = relationship("PCA", back_populates="itens")
    
    # Identificação do item
    numero_item = Column(Integer)
    categoria_item_pca_nome = Column(String(100))
    classificacao_catalogo_id = Column(String(10))
    nome_classificacao_catalogo = Column(String(50))
    
    # Classificação
    classificacao_superior_codigo = Column(String(100), index=True)
    classificacao_superior_nome = Column(String(255))
    pdm_codigo = Column(String(100))
    pdm_descricao = Column(String(255))
    
    # Descrição do item
    codigo_item = Column(String(100))
    descricao_item = Column(Text)
    unidade_fornecimento = Column(String(20))
    
    # Valores
    quantidade_estimada = Column(Decimal(15, 4))
    valor_unitario = Column(Decimal(15, 4))
    valor_total = Column(Decimal(15, 4))
    valor_orcamento_exercicio = Column(Decimal(15, 4))
    
    # Datas e informações complementares
    data_desejada = Column(Date)
    unidade_requisitante = Column(String(255))
    grupo_contratacao_codigo = Column(String(50))
    grupo_contratacao_nome = Column(String(255))
    data_inclusao = Column(Date)
    data_atualizacao = Column(Date)
Modelo Contratação


# app/models/contratacao.py
from sqlalchemy import Column, String, Integer, Decimal, Date, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel

class Contratacao(BaseModel):
    __tablename__ = "contratacao"
    
    # Identificação
    numero_controle_pncp = Column(String(50), unique=True, index=True)
    numero_compra = Column(String(50))
    ano_compra = Column(Integer, index=True)
    processo = Column(String(50))
    
    # Instrumento e modalidade
    tipo_instrumento_convocatorio_id = Column(Integer)
    tipo_instrumento_convocatorio_nome = Column(String(100))
    modalidade_id = Column(Integer, index=True)
    modalidade_nome = Column(String(100))
    modo_disputa_id = Column(Integer)
    modo_disputa_nome = Column(String(100))
    
    # Situação
    situacao_compra_id = Column(Integer, index=True)
    situacao_compra_nome = Column(String(100))
    
    # Objeto
    objeto_compra = Column(Text)
    informacao_complementar = Column(Text)
    srp = Column(Boolean, default=False)
    
    # Amparo legal
    amparo_legal_codigo = Column(Integer)
    amparo_legal_nome = Column(String(255))
    amparo_legal_descricao = Column(Text)
    
    # Valores
    valor_total_estimado = Column(Decimal(15, 4))
    valor_total_homologado = Column(Decimal(15, 4))
    
    # Datas
    data_abertura_proposta = Column(DateTime)
    data_encerramento_proposta = Column(DateTime, index=True)
    data_publicacao_pncp = Column(Date, index=True)
    data_inclusao = Column(Date)
    data_atualizacao = Column(Date)
    
    # Controle
    sequencial_compra = Column(Integer)
    
    # Órgão/Entidade
    orgao_entidade_cnpj = Column(String(14), index=True)
    orgao_entidade_razao_social = Column(String(255))
    orgao_entidade_poder_id = Column(String(1))
    orgao_entidade_esfera_id = Column(String(1))
    
    # Unidade do órgão
    unidade_orgao_codigo = Column(String(20))
    unidade_orgao_nome = Column(String(255))
    unidade_orgao_codigo_ibge = Column(Integer)
    unidade_orgao_municipio = Column(String(100))
    unidade_orgao_uf_sigla = Column(String(2), index=True)
    unidade_orgao_uf_nome = Column(String(50))
    
    # Órgão subrogado (opcional)
    orgao_subrogado_cnpj = Column(String(14))
    orgao_subrogado_razao_social = Column(String(255))
    orgao_subrogado_poder_id = Column(String(1))
    orgao_subrogado_esfera_id = Column(String(1))
    
    # Unidade subrogada (opcional)
    unidade_subrogada_codigo = Column(String(20))
    unidade_subrogada_nome = Column(String(255))
    unidade_subrogada_codigo_ibge = Column(Integer)
    unidade_subrogada_municipio = Column(String(100))
    unidade_subrogada_uf_sigla = Column(String(2))
    unidade_subrogada_uf_nome = Column(String(50))
    
    # Sistema
    usuario_nome = Column(String(255))
    link_sistema_origem = Column(String(500))
    justificativa_presencial = Column(Text)
    
    # Relacionamentos
    itens = relationship("ItemContratacao", back_populates="contratacao")

class ItemContratacao(BaseModel):
    __tablename__ = "item_contratacao"
    
    # Relacionamento
    contratacao_id = Column(Integer, ForeignKey("contratacao.id"))
    contratacao = relationship("Contratacao", back_populates="itens")
    
    # Identificação
    numero_item = Column(Integer)
    descricao_item = Column(Text)
    unidade_medida = Column(String(20))
    quantidade = Column(Decimal(15, 4))
    valor_unitario = Column(Decimal(15, 4))
    valor_total = Column(Decimal(15, 4))
    
    # Situação
    situacao_item_id = Column(Integer)
    situacao_item_nome = Column(String(100))
    
    # Benefícios
    tipo_beneficio_id = Column(Integer)
    tipo_beneficio_nome = Column(String(100))
Modelo Ata de Registro de Preços


# app/models/ata.py
from sqlalchemy import Column, String, Integer, Date, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class AtaRegistroPreco(BaseModel):
    __tablename__ = "ata_registro_preco"
    
    # Identificação
    numero_controle_pncp_ata = Column(String(50), unique=True, index=True)
    numero_controle_pncp_compra = Column(String(50), index=True)
    numero_ata_registro_preco = Column(String(50))
    ano_ata = Column(Integer, index=True)
    
    # Datas
    data_assinatura = Column(Date)
    vigencia_inicio = Column(Date, index=True)
    vigencia_fim = Column(Date, index=True)
    data_cancelamento = Column(Date)
    cancelado = Column(Boolean, default=False)
    data_publicacao_pncp = Column(Date)
    data_inclusao = Column(Date)
    data_atualizacao = Column(Date)
    
    # Objeto
    objeto_contratacao = Column(Text)
    
    # Órgão
    cnpj_orgao = Column(String(14), index=True)
    nome_orgao = Column(String(255))
    codigo_unidade_orgao = Column(String(20))
    nome_unidade_orgao = Column(String(255))
    
    # Órgão subrogado (opcional)
    cnpj_orgao_subrogado = Column(String(14))
    nome_orgao_subrogado = Column(String(255))
    codigo_unidade_orgao_subrogado = Column(String(20))
    nome_unidade_orgao_subrogado = Column(String(255))
    
    # Sistema
    usuario = Column(String(255))
Modelo Contrato


# app/models/contrato.py
from sqlalchemy import Column, String, Integer, Decimal, Date, DateTime, Text, Boolean
from .base import BaseModel

class Contrato(BaseModel):
    __tablename__ = "contrato"
    
    # Identificação
    numero_controle_pncp = Column(String(50), unique=True, index=True)
    numero_controle_pncp_compra = Column(String(50), index=True)
    numero_contrato_empenho = Column(String(50))
    ano_contrato = Column(Integer, index=True)
    sequencial_contrato = Column(Integer)
    processo = Column(String(50))
    
    # Tipo e categoria
    tipo_contrato_id = Column(Integer)
    tipo_contrato_nome = Column(String(100))
    categoria_processo_id = Column(Integer)
    categoria_processo_nome = Column(String(100))
    
    # Natureza
    receita = Column(Boolean, default=False)
    
    # Objeto
    objeto_contrato = Column(Text)
    informacao_complementar = Column(Text)
    
    # Órgão/Entidade
    orgao_entidade_cnpj = Column(String(14), index=True)
    orgao_entidade_razao_social = Column(String(255))
    orgao_entidade_poder_id = Column(String(1))
    orgao_entidade_esfera_id = Column(String(1))
    
    # Unidade executora
    unidade_orgao_codigo = Column(String(20))
    unidade_orgao_nome = Column(String(255))
    unidade_orgao_codigo_ibge = Column(Integer)
    unidade_orgao_municipio = Column(String(100))
    unidade_orgao_uf_sigla = Column(String(2))
    unidade_orgao_uf_nome = Column(String(50))
    
    # Órgão subrogado
    orgao_subrogado_cnpj = Column(String(14))
    orgao_subrogado_razao_social = Column(String(255))
    orgao_subrogado_poder_id = Column(String(1))
    orgao_subrogado_esfera_id = Column(String(1))
    
    # Unidade subrogada
    unidade_subrogada_codigo = Column(String(20))
    unidade_subrogada_nome = Column(String(255))
    unidade_subrogada_codigo_ibge = Column(Integer)
    unidade_subrogada_municipio = Column(String(100))
    unidade_subrogada_uf_sigla = Column(String(2))
    unidade_subrogada_uf_nome = Column(String(50))
    
    # Fornecedor
    tipo_pessoa = Column(String(2))
    ni_fornecedor = Column(String(30))
    nome_razao_social_fornecedor = Column(String(100))
    
    # Subcontratado (opcional)
    tipo_pessoa_subcontratada = Column(String(2))
    ni_fornecedor_subcontratado = Column(String(30))
    nome_fornecedor_subcontratado = Column(String(100))
    
    # Valores
    valor_inicial = Column(Decimal(15, 4))
    numero_parcelas = Column(Integer)
    valor_parcela = Column(Decimal(15, 4))
    valor_global = Column(Decimal(15, 4))
    valor_acumulado = Column(Decimal(15, 4))
    
    # Datas
    data_assinatura = Column(Date)
    data_vigencia_inicio = Column(Date, index=True)
    data_vigencia_fim = Column(Date, index=True)
    data_publicacao_pncp = Column(DateTime)
    data_atualizacao = Column(DateTime)
    
    # Controle
    numero_retificacao = Column(Integer)
    
    # Sistema
    usuario_nome = Column(String(255))
    
    # CIPI (opcional)
    identificador_cipi = Column(String(100))
    url_cipi = Column(String(500))
Constantes e Tabelas de Domínio


# app/utils/constants.py
from enum import Enum

class InstrumentoConvocatorio(Enum):
    EDITAL = 1
    AVISO_CONTRATACAO_DIRETA = 2
    ATO_AUTORIZA_CONTRATACAO_DIRETA = 3

class ModalidadeContratacao(Enum):
    LEILAO_ELETRONICO = 1
    DIALOGO_COMPETITIVO = 2
    CONCURSO = 3
    CONCORRENCIA_ELETRONICA = 4
    CONCORRENCIA_PRESENCIAL = 5
    PREGAO_ELETRONICO = 6
    PREGAO_PRESENCIAL = 7
    DISPENSA_LICITACAO = 8
    INEXIGIBILIDADE = 9
    MANIFESTACAO_INTERESSE = 10
    PRE_QUALIFICACAO = 11
    CREDENCIAMENTO = 12
    LEILAO_PRESENCIAL = 13

class ModoDisputa(Enum):
    ABERTO = 1
    FECHADO = 2
    ABERTO_FECHADO = 3
    DISPENSA_COM_DISPUTA = 4
    NAO_SE_APLICA = 5
    FECHADO_ABERTO = 6

class CriterioJulgamento(Enum):
    MENOR_PRECO = 1
    MAIOR_DESCONTO = 2
    TECNICA_PRECO = 4
    MAIOR_LANCE = 5
    MAIOR_RETORNO_ECONOMICO = 6
    NAO_SE_APLICA = 7
    MELHOR_TECNICA = 8
    CONTEUDO_ARTISTICO = 9

class SituacaoContratacao(Enum):
    DIVULGADA_PNCP = 1
    REVOGADA = 2
    ANULADA = 3
    SUSPENSA = 4

class SituacaoItem(Enum):
    EM_ANDAMENTO = 1
    HOMOLOGADO = 2
    ANULADO_REVOGADO_CANCELADO = 3
    DESERTO = 4
    FRACASSADO = 5

class TipoBeneficio(Enum):
    PARTICIPACAO_EXCLUSIVA_ME_EPP = 1
    SUBCONTRATACAO_ME_EPP = 2
    COTA_RESERVADA_ME_EPP = 3
    SEM_BENEFICIO = 4
    NAO_SE_APLICA = 5

class TipoContrato(Enum):
    CONTRATO_TERMO_INICIAL = 1
    COMODATO = 2
    ARRENDAMENTO = 3
    CONCESSAO = 4
    TERMO_ADESAO = 5
    CONVENIO = 6
    EMPENHO = 7
    OUTROS = 8
    TED = 9
    ACT = 10
    TERMO_COMPROMISSO = 11
    CARTA_CONTRATO = 12

class PorteEmpresa(Enum):
    ME = 1
    EPP = 2
    DEMAIS = 3
    NAO_SE_APLICA = 4
    NAO_INFORMADO = 5

class CategoriaProcesso(Enum):
    CESSAO = 1
    COMPRAS = 2
    INFORMATICA_TIC = 3
    INTERNACIONAL = 4
    LOCACAO_IMOVEIS = 5
    MAO_OBRA = 6
    OBRAS = 7
    SERVICOS = 8
    SERVICOS_ENGENHARIA = 9
    SERVICOS_SAUDE = 10
    ALIENACAO_BENS = 11

class CategoriaItemPCA(Enum):
    MATERIAL = 1
    SERVICO = 2
    OBRAS = 3
    SERVICOS_ENGENHARIA = 4
    SOLUCOES_TIC = 5
    LOCACAO_IMOVEIS = 6
    ALIENACAO_CONCESSAO_PERMISSAO = 7
    OBRAS_SERVICOS_ENGENHARIA = 8

# Mapeamento para consultas
MODALIDADE_NAMES = {
    1: "Leilão Eletrônico",
    2: "Diálogo Competitivo", 
    3: "Concurso",
    4: "Concorrência Eletrônica",
    5: "Concorrência Presencial",
    6: "Pregão Eletrônico",
    7: "Pregão Presencial",
    8: "Dispensa de Licitação",
    9: "Inexigibilidade",
    10: "Manifestação de Interesse",
    11: "Pré-qualificação",
    12: "Credenciamento",
    13: "Leilão Presencial"
}

SITUACAO_CONTRATACAO_NAMES = {
    1: "Divulgada no PNCP",
    2: "Revogada",
    3: "Anulada", 
    4: "Suspensa"
}

AMPARO_LEGAL_NAMES = {
    1: "Lei 14.133/2021, Art. 28, I",
    2: "Lei 14.133/2021, Art. 28, II",
    3: "Lei 14.133/2021, Art. 28, III",
    4: "Lei 14.133/2021, Art. 28, IV",
    5: "Lei 14.133/2021, Art. 28, V",
    6: "Lei 14.133/2021, Art. 74, I",
    7: "Lei 14.133/2021, Art. 74, II",
    8: "Lei 14.133/2021, Art. 74, III, a",
    # ... demais códigos conforme tabela do PNCP
}
Schemas Pydantic

Schemas Comuns


# app/schemas/common.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal

class PaginationParams(BaseModel):
    pagina: int = Field(1, ge=1, description="Número da página")
    tamanho_pagina: int = Field(50, ge=1, le=500, description="Tamanho da página")

class PaginatedResponse(BaseModel):
    data: List[Any]
    total_registros: int
    total_paginas: int
    numero_pagina: int
    paginas_restantes: int
    empty: bool

class DateRangeFilter(BaseModel):
    data_inicial: date = Field(..., description="Data inicial no formato YYYY-MM-DD")
    data_final: date = Field(..., description="Data final no formato YYYY-MM-DD")
    
    @validator('data_final')
    def validate_date_range(cls, v, values):
        if 'data_inicial' in values and v < values['data_inicial']:
            raise ValueError('Data final deve ser maior que data inicial')
        return v

class OrgaoEntidade(BaseModel):
    cnpj: str = Field(..., max_length=14, description="CNPJ do órgão")
    razao_social: str = Field(..., max_length=255, description="Razão social")
    poder_id: Optional[str] = Field(None, max_length=1, description="L/E/J")
    esfera_id: Optional[str] = Field(None, max_length=1, description="F/E/M/D")

class UnidadeOrgao(BaseModel):
    codigo_unidade: str = Field(..., max_length=20, description="Código da unidade")
    nome_unidade: str = Field(..., max_length=255, description="Nome da unidade")
    codigo_ibge: Optional[int] = Field(None, description="Código IBGE município")
    municipio_nome: Optional[str] = Field(None, max_length=100, description="Nome município")
    uf_sigla: Optional[str] = Field(None, max_length=2, description="UF")
    uf_nome: Optional[str] = Field(None, max_length=50, description="Nome UF")

class AmparoLegal(BaseModel):
    codigo: int = Field(..., description="Código do amparo legal")
    nome: str = Field(..., max_length=255, description="Nome do amparo legal")
    descricao: Optional[str] = Field(None, description="Descrição do amparo legal")
Schemas PCA


# app/schemas/pca.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date
from decimal import Decimal
from .common import PaginationParams, OrgaoEntidade, UnidadeOrgao

class PCAFilters(BaseModel):
    ano_pca: int = Field(..., ge=2000, le=2050, description="Ano do PCA")
    id_usuario: Optional[int] = Field(None, description="ID do usuário/sistema")
    codigo_classificacao_superior: Optional[str] = Field(None, max_length=100, description="Código da classificação superior")
    
class ItemPCAResponse(BaseModel):
    numero_item: int
    categoria_item_pca_nome: str
    classificacao_catalogo_id: str
    nome_classificacao_catalogo: str
    classificacao_superior_codigo: Optional[str]
    classificacao_superior_nome: Optional[str]
    pdm_codigo: Optional[str]
    pdm_descricao: Optional[str]
    codigo_item: str
    descricao_item: str
    unidade_fornecimento: str
    quantidade_estim
            raise ValueError('Data final deve ser maior que data inicial')
        return v

class OrgaoEntidade(BaseModel):
    cnpj: str = Field(..., max_length=14, description="CNPJ do órgão")
    razao_social: str = Field(..., max_length=255, description="Razão social")
    poder_id: Optional[str] = Field(None, max_length=1, description="L/E/J")
    esfera_id: Optional[str] = Field(None, max_length=1, description="F/E/M/D")

class UnidadeOrgao(BaseModel):
    codigo_unidade: str = Field(..., max_length=20, description="Código da unidade")
    nome_unidade: str = Field(..., max_length=255, description="Nome da unidade")
    codigo_ibge: Optional[int] = Field(None, description="Código IBGE município")
    municipio_nome: Optional[str] = Field(None, max_length=100, description="Nome município")
    uf_sigla: Optional[str] = Field(None, max_length=2, description="UF")
    uf_nome: Optional[str] = Field(None, max_length=50, description="Nome UF")

class AmparoLegal(BaseModel):
    codigo: int = Field(..., description="Código do amparo legal")
    nome: str = Field(..., max_length=255, description="Nome do amparo legal")
    descricao: Optional[str] = Field(None, description="Descrição do amparo legal")
Schemas PCA


# app/schemas/pca.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date
from decimal import Decimal
from .common import PaginationParams, OrgaoEntidade, UnidadeOrgao

class PCAFilters(BaseModel):
    ano_pca: int = Field(..., ge=2000, le=2050, description="Ano do PCA")
    id_usuario: Optional[int] = Field(None, description="ID do usuário/sistema")
    codigo_classificacao_superior: Optional[str] = Field(None, max_length=100, description="Código da classificação superior")
    
class ItemPCAResponse(BaseModel):
    numero_item: int
    categoria_item_pca_nome: str
    classificacao_catalogo_id: str
    nome_classificacao_catalogo: str
    classificacao_superior_codigo: Optional[str]
    classificacao_superior_nome: Optional[str]
    pdm_codigo: Optional[str]
    pdm_descricao: Optional[str]
    codigo_item: str
    descricao_item: str
    unidade_fornecimento: str
    quantidade_estim

