import redis
import json
import pickle
from typing import Optional, Any, Dict, List, Union
import logging
from datetime import datetime, timedelta

from .config import settings

logger = logging.getLogger(__name__)

# Redis client configuration
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True
)


class CacheService:
    """Service for handling Redis cache operations."""
    
    def __init__(self):
        self.client = redis_client
        self.default_ttl = settings.CACHE_TTL
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache GET error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        try:
            serialized_value = json.dumps(value, default=str)
            ttl = ttl or self.default_ttl
            return self.client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Cache SET error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Cache DELETE error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Cache EXISTS error for key {key}: {e}")
            return False
    
    def generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from prefix and parameters."""
        params = "_".join([f"{k}:{v}" for k, v in sorted(kwargs.items()) if v is not None])
        return f"{prefix}:{params}" if params else prefix
    
    async def get_or_set(self, key: str, func, ttl: Optional[int] = None) -> Any:
        """Get from cache or set using function result."""
        value = await self.get(key)
        if value is not None:
            return value
        
        # Execute function and cache result
        result = func() if callable(func) else func
        await self.set(key, result, ttl)
        return result
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache CLEAR_PATTERN error for pattern {pattern}: {e}")
            return 0
    
    def health_check(self) -> bool:
        """Check Redis connection health."""
        try:
            self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False


class DomainCacheService:
    """Service for caching domain tables and lookup data."""
    
    def __init__(self):
        self.cache = CacheService()
        self.domain_ttl = settings.DOMAIN_CACHE_TTL
    
    async def get_modalidades_contratacao(self) -> Dict[int, str]:
        """Get modalidades de contratação from cache."""
        key = "domain:modalidades_contratacao"
        cached = await self.cache.get(key)
        
        if cached:
            return cached
        
        # Default modalidades based on Lei 14.133/2021
        modalidades = {
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
            17: "Compras Governamentais",
        }
        
        await self.cache.set(key, modalidades, self.domain_ttl)
        return modalidades
    
    async def get_situacoes_contratacao(self) -> Dict[int, str]:
        """Get situações de contratação from cache."""
        key = "domain:situacoes_contratacao"
        cached = await self.cache.get(key)
        
        if cached:
            return cached
        
        situacoes = {
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
            15: "Republicada",
        }
        
        await self.cache.set(key, situacoes, self.domain_ttl)
        return situacoes
    
    async def get_tipos_contrato(self) -> Dict[int, str]:
        """Get tipos de contrato from cache."""
        key = "domain:tipos_contrato"
        cached = await self.cache.get(key)
        
        if cached:
            return cached
        
        tipos = {
            1: "Compra",
            2: "Serviço",
            3: "Obra",
            4: "Serviço de Engenharia",
            5: "Concessão",
            6: "Permissão",
            7: "Alienação",
            8: "Locação",
            9: "Fornecimento",
            10: "Prestação de Serviço",
        }
        
        await self.cache.set(key, tipos, self.domain_ttl)
        return tipos
    
    async def update_all_caches(self):
        """Update all domain caches."""
        await self.get_modalidades_contratacao()
        await self.get_situacoes_contratacao()
        await self.get_tipos_contrato()
        logger.info("Domain caches updated successfully")


async def delete_cache_pattern(pattern: str):
    """
    Deleta chaves de cache que correspondem ao padrão
    """
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Deleted {len(keys)} cache keys matching pattern: {pattern}")
    except Exception as e:
        logger.error(f"Error deleting cache pattern {pattern}: {e}")


async def clear_cache_pattern(pattern: str):
    """
    Limpa padrão de cache (alias para delete_cache_pattern)
    """
    await delete_cache_pattern(pattern)


# Global cache instances
cache = CacheService()
domain_cache = DomainCacheService()

# Global cache instance
cache_service = CacheService()

# Helper functions for simpler API
async def get_cache(key: str) -> Optional[Any]:
    """Helper function to get value from cache."""
    return await cache_service.get(key)

async def set_cache(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Helper function to set value in cache with optional TTL."""
    return await cache_service.set(key, value, ttl)

async def delete_cache(key: str) -> bool:
    """Helper function to delete key from cache."""
    return await cache_service.delete(key)
