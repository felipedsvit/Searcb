"""
Configuração de testes
"""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# Configurar variáveis de ambiente para testes
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["TESTING"] = "true"

# Configurar banco de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """
    Override da função get_db para testes
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db_engine():
    """
    Fixture para engine do banco de dados
    """
    return engine


@pytest.fixture(scope="session")
def db_session():
    """
    Fixture para sessão do banco de dados
    """
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    # Criar sessão
    session = TestingSessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """
    Fixture para cliente de teste
    """
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user():
    """
    Fixture para usuário mock
    """
    return type('MockUser', (), {
        'id': 1,
        'email': 'test@example.com',
        'is_admin': False,
        'ativo': True,
        'pode_criar_pca': True,
        'pode_criar_contratacao': True,
        'pode_criar_ata': True,
        'pode_criar_contrato': True,
        'pode_prorrogar_contrato': True
    })()


@pytest.fixture
def mock_admin():
    """
    Fixture para admin mock
    """
    return type('MockUser', (), {
        'id': 1,
        'email': 'admin@example.com',
        'is_admin': True,
        'ativo': True,
        'pode_criar_pca': True,
        'pode_criar_contratacao': True,
        'pode_criar_ata': True,
        'pode_criar_contrato': True,
        'pode_prorrogar_contrato': True
    })()


@pytest.fixture
def auth_headers():
    """
    Fixture para headers de autenticação
    """
    return {"Authorization": "Bearer fake-token-for-tests"}


@pytest.fixture
def sample_pca_data():
    """
    Fixture para dados de PCA de exemplo
    """
    return {
        "orgao_cnpj": "12345678000100",
        "orgao_nome": "Órgão de Teste",
        "ano": 2024,
        "valor_total": 1000000.00,
        "data_publicacao": "2024-01-15",
        "status": "ATIVO",
        "titulo": "PCA de Teste",
        "descricao": "Descrição do PCA de teste"
    }


@pytest.fixture
def sample_contratacao_data():
    """
    Fixture para dados de contratação de exemplo
    """
    return {
        "numero_compra": "COMP-2024-001",
        "orgao_cnpj": "12345678000100",
        "orgao_nome": "Órgão de Teste",
        "modalidade": "PREGAO_ELETRONICO",
        "situacao": "ABERTA",
        "objeto_contratacao": "Objeto de teste",
        "valor_total_estimado": 500000.00,
        "data_abertura_proposta": "2024-01-15T10:00:00",
        "data_encerramento_proposta": "2024-01-25T18:00:00"
    }


@pytest.fixture
def sample_ata_data():
    """
    Fixture para dados de ata de exemplo
    """
    return {
        "numero_ata": "ATA-2024-001",
        "orgao_cnpj": "12345678000100",
        "orgao_nome": "Órgão de Teste",
        "objeto": "Objeto da ata",
        "valor_total": 300000.00,
        "data_publicacao": "2024-01-15",
        "data_inicio_vigencia": "2024-02-01",
        "data_fim_vigencia": "2024-12-31",
        "situacao": "VIGENTE"
    }


@pytest.fixture
def sample_contrato_data():
    """
    Fixture para dados de contrato de exemplo
    """
    return {
        "numero_contrato": "CONT-2024-001",
        "orgao_cnpj": "12345678000100",
        "orgao_nome": "Órgão de Teste",
        "fornecedor_cnpj": "98765432000100",
        "fornecedor_nome": "Fornecedor de Teste",
        "objeto": "Objeto do contrato",
        "valor_inicial": 100000.00,
        "data_assinatura": "2024-01-15",
        "data_inicio_vigencia": "2024-02-01",
        "data_fim_vigencia": "2024-12-31",
        "situacao": "ATIVO"
    }


# Configuração para pytest
def pytest_configure(config):
    """
    Configuração personalizada do pytest
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# Configuração para logging em testes
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Reduzir verbosidade de alguns loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
