from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sistema PNCP - Gestão Pública"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API para integração com Portal Nacional de Contratações Públicas"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://pncp_user:pncp_password@localhost:5432/pncp_db"
    )
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # PNCP API Configuration
    PNCP_API_URL: str = "https://pncp.gov.br/api/consulta"
    PNCP_TIMEOUT: int = 30
    PNCP_WEBHOOK_SECRET: str = os.getenv("PNCP_WEBHOOK_SECRET", "webhook-secret-key")
    
    # Pagination Configuration
    MAX_PAGE_SIZE: int = 500
    DEFAULT_PAGE_SIZE: int = 50
    
    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Cache Configuration
    CACHE_TTL: int = 3600  # 1 hour
    DOMAIN_CACHE_TTL: int = 86400  # 24 hours
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",      # React dev server (common)
        "http://localhost:8080",      # Vue dev server (common)
        "http://localhost:5173",      # Vite dev server (common)
        "http://localhost:5174",      # Current frontend port
        "https://localhost:3000",
        "https://localhost:8080",
        "https://localhost:5173",
        "https://localhost:5174",
    ]
    
    # Celery Configuration
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PATH: str = "/metrics"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
