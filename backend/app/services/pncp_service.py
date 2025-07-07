"""
Serviço para integração com APIs do PNCP (Portal Nacional de Contratações Públicas)
"""
import httpx
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import json
import logging
from urllib.parse import urlencode

from app.core.config import settings
from app.core.cache import cache
from app.utils.helpers import format_cnpj, validate_cnpj

logger = logging.getLogger(__name__)


class PNCPService:
    """
    Serviço para integração com o PNCP
    """
    
    def __init__(self):
        self.base_url = settings.PNCP_API_URL
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 1
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Faz requisição HTTP para o PNCP com retry automático
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        default_headers = {
            "User-Agent": "SEARCB-Backend/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if headers:
            default_headers.update(headers)
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        params=params,
                        json=data,
                        headers=default_headers
                    )
                    
                    response.raise_for_status()
                    
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {"data": response.text}
                        
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                if e.response.status_code == 429:  # Rate limit
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise
        
        raise Exception(f"Failed to make request after {self.max_retries} attempts")
    
    async def obter_pcas(
        self,
        cnpj_orgao: Optional[str] = None,
        ano: Optional[int] = None,
        pagina: int = 1,
        tamanho: int = 20
    ) -> Dict[str, Any]:
        """
        Obtém lista de PCAs do PNCP
        """
        cache_key = f"pncp_pcas_{cnpj_orgao}_{ano}_{pagina}_{tamanho}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        params = {
            "pagina": pagina,
            "tamanhoPagina": tamanho
        }
        
        if cnpj_orgao:
            params["cnpj"] = format_cnpj(cnpj_orgao)
        
        if ano:
            params["ano"] = ano
        
        try:
            result = await self._make_request("GET", "pca", params=params)
            
            # Cache por 1 hora
            await cache.set(cache_key, result, ttl=3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter PCAs do PNCP: {e}")
            raise
    
    async def obter_pca_por_id(self, pca_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de um PCA específico
        """
        cache_key = f"pncp_pca_{pca_id}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            result = await self._make_request("GET", f"pca/{pca_id}")
            
            # Cache por 2 horas
            await cache.set(cache_key, result, ttl=7200)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter PCA {pca_id} do PNCP: {e}")
            raise
    
    async def obter_contratacoes(
        self,
        cnpj_orgao: Optional[str] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        modalidade: Optional[str] = None,
        pagina: int = 1,
        tamanho: int = 20
    ) -> Dict[str, Any]:
        """
        Obtém lista de contratações do PNCP
        """
        cache_key = f"pncp_contratacoes_{cnpj_orgao}_{data_inicio}_{data_fim}_{modalidade}_{pagina}_{tamanho}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        params = {
            "pagina": pagina,
            "tamanhoPagina": tamanho
        }
        
        if cnpj_orgao:
            params["cnpj"] = format_cnpj(cnpj_orgao)
        
        if data_inicio:
            params["dataInicio"] = data_inicio.strftime("%Y-%m-%d")
        
        if data_fim:
            params["dataFim"] = data_fim.strftime("%Y-%m-%d")
        
        if modalidade:
            params["modalidade"] = modalidade
        
        try:
            result = await self._make_request("GET", "contratacoes", params=params)
            
            # Cache por 30 minutos
            await cache.set(cache_key, result, ttl=1800)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter contratações do PNCP: {e}")
            raise
    
    async def obter_contratacao_por_id(self, contratacao_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de uma contratação específica
        """
        cache_key = f"pncp_contratacao_{contratacao_id}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            result = await self._make_request("GET", f"contratacoes/{contratacao_id}")
            
            # Cache por 1 hora
            await cache.set(cache_key, result, ttl=3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter contratação {contratacao_id} do PNCP: {e}")
            raise
    
    async def obter_atas(
        self,
        cnpj_orgao: Optional[str] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        pagina: int = 1,
        tamanho: int = 20
    ) -> Dict[str, Any]:
        """
        Obtém lista de atas do PNCP
        """
        cache_key = f"pncp_atas_{cnpj_orgao}_{data_inicio}_{data_fim}_{pagina}_{tamanho}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        params = {
            "pagina": pagina,
            "tamanhoPagina": tamanho
        }
        
        if cnpj_orgao:
            params["cnpj"] = format_cnpj(cnpj_orgao)
        
        if data_inicio:
            params["dataInicio"] = data_inicio.strftime("%Y-%m-%d")
        
        if data_fim:
            params["dataFim"] = data_fim.strftime("%Y-%m-%d")
        
        try:
            result = await self._make_request("GET", "atas", params=params)
            
            # Cache por 1 hora
            await cache.set(cache_key, result, ttl=3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter atas do PNCP: {e}")
            raise
    
    async def obter_ata_por_id(self, ata_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de uma ata específica
        """
        cache_key = f"pncp_ata_{ata_id}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            result = await self._make_request("GET", f"atas/{ata_id}")
            
            # Cache por 2 horas
            await cache.set(cache_key, result, ttl=7200)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter ata {ata_id} do PNCP: {e}")
            raise
    
    async def obter_contratos(
        self,
        cnpj_orgao: Optional[str] = None,
        cnpj_fornecedor: Optional[str] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        pagina: int = 1,
        tamanho: int = 20
    ) -> Dict[str, Any]:
        """
        Obtém lista de contratos do PNCP
        """
        cache_key = f"pncp_contratos_{cnpj_orgao}_{cnpj_fornecedor}_{data_inicio}_{data_fim}_{pagina}_{tamanho}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        params = {
            "pagina": pagina,
            "tamanhoPagina": tamanho
        }
        
        if cnpj_orgao:
            params["cnpjOrgao"] = format_cnpj(cnpj_orgao)
        
        if cnpj_fornecedor:
            params["cnpjFornecedor"] = format_cnpj(cnpj_fornecedor)
        
        if data_inicio:
            params["dataInicio"] = data_inicio.strftime("%Y-%m-%d")
        
        if data_fim:
            params["dataFim"] = data_fim.strftime("%Y-%m-%d")
        
        try:
            result = await self._make_request("GET", "contratos", params=params)
            
            # Cache por 30 minutos
            await cache.set(cache_key, result, ttl=1800)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter contratos do PNCP: {e}")
            raise
    
    async def obter_contrato_por_id(self, contrato_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de um contrato específico
        """
        cache_key = f"pncp_contrato_{contrato_id}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            result = await self._make_request("GET", f"contratos/{contrato_id}")
            
            # Cache por 1 hora
            await cache.set(cache_key, result, ttl=3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter contrato {contrato_id} do PNCP: {e}")
            raise
    
    async def obter_orgaos(
        self,
        uf: Optional[str] = None,
        municipio: Optional[str] = None,
        pagina: int = 1,
        tamanho: int = 50
    ) -> Dict[str, Any]:
        """
        Obtém lista de órgãos do PNCP
        """
        cache_key = f"pncp_orgaos_{uf}_{municipio}_{pagina}_{tamanho}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        params = {
            "pagina": pagina,
            "tamanhoPagina": tamanho
        }
        
        if uf:
            params["uf"] = uf.upper()
        
        if municipio:
            params["municipio"] = municipio
        
        try:
            result = await self._make_request("GET", "orgaos", params=params)
            
            # Cache por 24 horas (dados menos voláteis)
            await cache.set(cache_key, result, ttl=86400)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter órgãos do PNCP: {e}")
            raise
    
    async def obter_orgao_por_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """
        Obtém detalhes de um órgão específico por CNPJ
        """
        cnpj_formatado = format_cnpj(cnpj)
        cache_key = f"pncp_orgao_{cnpj_formatado}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            result = await self._make_request("GET", f"orgaos/{cnpj_formatado}")
            
            # Cache por 24 horas
            await cache.set(cache_key, result, ttl=86400)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter órgão {cnpj} do PNCP: {e}")
            raise
    
    async def obter_modalidades(self) -> List[Dict[str, str]]:
        """
        Obtém lista de modalidades de contratação
        """
        cache_key = "pncp_modalidades"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            result = await self._make_request("GET", "modalidades")
            
            # Cache por 7 dias (dados estáticos)
            await cache.set(cache_key, result, ttl=604800)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter modalidades do PNCP: {e}")
            raise
    
    async def obter_situacoes(self) -> List[Dict[str, str]]:
        """
        Obtém lista de situações de contratação
        """
        cache_key = "pncp_situacoes"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            result = await self._make_request("GET", "situacoes")
            
            # Cache por 7 dias (dados estáticos)
            await cache.set(cache_key, result, ttl=604800)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter situações do PNCP: {e}")
            raise
    
    async def buscar_por_termo(
        self,
        termo: str,
        tipo: Optional[str] = None,
        pagina: int = 1,
        tamanho: int = 20
    ) -> Dict[str, Any]:
        """
        Busca por termo livre no PNCP
        """
        cache_key = f"pncp_busca_{termo}_{tipo}_{pagina}_{tamanho}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        params = {
            "q": termo,
            "pagina": pagina,
            "tamanhoPagina": tamanho
        }
        
        if tipo:
            params["tipo"] = tipo
        
        try:
            result = await self._make_request("GET", "buscar", params=params)
            
            # Cache por 15 minutos
            await cache.set(cache_key, result, ttl=900)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao buscar '{termo}' no PNCP: {e}")
            raise
    
    async def sincronizar_dados(
        self,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Sincroniza dados do PNCP em lote
        """
        if not data_inicio:
            data_inicio = date.today().replace(day=1)  # Primeiro dia do mês
        
        if not data_fim:
            data_fim = date.today()
        
        logger.info(f"Iniciando sincronização PNCP: {data_inicio} a {data_fim}")
        
        resultados = {
            "pcas": 0,
            "contratacoes": 0,
            "atas": 0,
            "contratos": 0,
            "erros": []
        }
        
        try:
            # Sincronizar PCAs
            pcas_result = await self.obter_pcas(
                data_inicio=data_inicio,
                data_fim=data_fim,
                tamanho=100
            )
            resultados["pcas"] = len(pcas_result.get("data", []))
            
            # Sincronizar Contratações
            contratacoes_result = await self.obter_contratacoes(
                data_inicio=data_inicio,
                data_fim=data_fim,
                tamanho=100
            )
            resultados["contratacoes"] = len(contratacoes_result.get("data", []))
            
            # Sincronizar Atas
            atas_result = await self.obter_atas(
                data_inicio=data_inicio,
                data_fim=data_fim,
                tamanho=100
            )
            resultados["atas"] = len(atas_result.get("data", []))
            
            # Sincronizar Contratos
            contratos_result = await self.obter_contratos(
                data_inicio=data_inicio,
                data_fim=data_fim,
                tamanho=100
            )
            resultados["contratos"] = len(contratos_result.get("data", []))
            
            logger.info(f"Sincronização concluída: {resultados}")
            
        except Exception as e:
            error_msg = f"Erro na sincronização: {e}"
            logger.error(error_msg)
            resultados["erros"].append(error_msg)
        
        return resultados


# Instância global do serviço
pncp_service = PNCPService()
