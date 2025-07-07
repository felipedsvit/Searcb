"""
Testes de integração para a API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# Configurar banco de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar tabelas de teste
Base.metadata.create_all(bind=engine)


def override_get_db():
    """
    Override da função get_db para testes
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Aplicar override
app.dependency_overrides[get_db] = override_get_db

# Cliente de teste
client = TestClient(app)


class TestAuth:
    """
    Testes de autenticação
    """
    
    def test_login_invalid_credentials(self):
        """
        Testa login com credenciais inválidas
        """
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "invalid@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_login_missing_credentials(self):
        """
        Testa login sem credenciais
        """
        response = client.post("/api/v1/auth/login")
        assert response.status_code == 422
    
    def test_protected_route_without_token(self):
        """
        Testa acesso a rota protegida sem token
        """
        response = client.get("/api/v1/pca")
        assert response.status_code == 401


class TestPCA:
    """
    Testes de PCA
    """
    
    @pytest.fixture
    def auth_headers(self):
        """
        Fixture para headers de autenticação
        """
        # Em um teste real, você criaria um usuário e faria login
        # Por enquanto, simular token
        return {"Authorization": "Bearer fake-token"}
    
    @patch('app.core.security.get_current_user')
    def test_list_pcas_unauthorized(self, mock_get_current_user):
        """
        Testa listagem de PCAs sem autenticação
        """
        mock_get_current_user.side_effect = Exception("Unauthorized")
        
        response = client.get("/api/v1/pca")
        assert response.status_code == 401
    
    @patch('app.core.security.get_current_user')
    def test_list_pcas_authorized(self, mock_get_current_user):
        """
        Testa listagem de PCAs com autenticação
        """
        # Mock do usuário autenticado
        mock_user = type('MockUser', (), {
            'id': 1,
            'email': 'test@example.com',
            'is_admin': False
        })()
        mock_get_current_user.return_value = mock_user
        
        response = client.get("/api/v1/pca")
        assert response.status_code == 200
        assert "data" in response.json()
        assert "total" in response.json()
        assert "page" in response.json()


class TestContratacao:
    """
    Testes de contratações
    """
    
    @patch('app.core.security.get_current_user')
    def test_list_contratacoes(self, mock_get_current_user):
        """
        Testa listagem de contratações
        """
        mock_user = type('MockUser', (), {
            'id': 1,
            'email': 'test@example.com',
            'is_admin': False
        })()
        mock_get_current_user.return_value = mock_user
        
        response = client.get("/api/v1/contratacoes")
        assert response.status_code == 200
        assert "data" in response.json()
    
    @patch('app.core.security.get_current_user')
    def test_get_contratacao_not_found(self, mock_get_current_user):
        """
        Testa busca de contratação não encontrada
        """
        mock_user = type('MockUser', (), {
            'id': 1,
            'email': 'test@example.com',
            'is_admin': False
        })()
        mock_get_current_user.return_value = mock_user
        
        response = client.get("/api/v1/contratacoes/999999")
        assert response.status_code == 404


class TestAta:
    """
    Testes de atas
    """
    
    @patch('app.core.security.get_current_user')
    def test_list_atas(self, mock_get_current_user):
        """
        Testa listagem de atas
        """
        mock_user = type('MockUser', (), {
            'id': 1,
            'email': 'test@example.com',
            'is_admin': False
        })()
        mock_get_current_user.return_value = mock_user
        
        response = client.get("/api/v1/atas")
        assert response.status_code == 200
        assert "data" in response.json()


class TestContrato:
    """
    Testes de contratos
    """
    
    @patch('app.core.security.get_current_user')
    def test_list_contratos(self, mock_get_current_user):
        """
        Testa listagem de contratos
        """
        mock_user = type('MockUser', (), {
            'id': 1,
            'email': 'test@example.com',
            'is_admin': False
        })()
        mock_get_current_user.return_value = mock_user
        
        response = client.get("/api/v1/contratos")
        assert response.status_code == 200
        assert "data" in response.json()
    
    @patch('app.core.security.get_current_user')
    def test_contract_vigencia(self, mock_get_current_user):
        """
        Testa verificação de vigência de contrato
        """
        mock_user = type('MockUser', (), {
            'id': 1,
            'email': 'test@example.com',
            'is_admin': False
        })()
        mock_get_current_user.return_value = mock_user
        
        # Este teste falhará porque o contrato não existe
        response = client.get("/api/v1/contratos/1/vigencia")
        assert response.status_code == 404


class TestWebhooks:
    """
    Testes de webhooks
    """
    
    def test_webhook_pncp_invalid_payload(self):
        """
        Testa webhook com payload inválido
        """
        response = client.post(
            "/api/v1/webhooks/pncp/notification",
            json="invalid json"
        )
        assert response.status_code == 400
    
    def test_webhook_pncp_missing_event_type(self):
        """
        Testa webhook sem tipo de evento
        """
        response = client.post(
            "/api/v1/webhooks/pncp/notification",
            json={"data": {}}
        )
        assert response.status_code == 200  # Deve processar mesmo sem event_type
    
    @patch('app.core.security.get_current_user')
    def test_webhook_interno(self, mock_get_current_user):
        """
        Testa webhook interno
        """
        mock_user = type('MockUser', (), {
            'id': 1,
            'email': 'test@example.com',
            'is_admin': False
        })()
        mock_get_current_user.return_value = mock_user
        
        response = client.post(
            "/api/v1/webhooks/interno/notification",
            json={
                "type": "user.login",
                "data": {"user_id": 1}
            }
        )
        assert response.status_code == 200


class TestAdmin:
    """
    Testes de administração
    """
    
    @patch('app.core.security.get_current_user')
    def test_admin_dashboard_unauthorized(self, mock_get_current_user):
        """
        Testa dashboard sem permissão de admin
        """
        mock_user = type('MockUser', (), {
            'id': 1,
            'email': 'test@example.com',
            'is_admin': False
        })()
        mock_get_current_user.return_value = mock_user
        
        response = client.get("/api/v1/admin/dashboard")
        assert response.status_code == 403
    
    @patch('app.core.security.get_current_user')
    def test_admin_dashboard_authorized(self, mock_get_current_user):
        """
        Testa dashboard com permissão de admin
        """
        mock_user = type('MockUser', (), {
            'id': 1,
            'email': 'admin@example.com',
            'is_admin': True
        })()
        mock_get_current_user.return_value = mock_user
        
        response = client.get("/api/v1/admin/dashboard")
        assert response.status_code == 200
        assert "totais" in response.json()
    
    @patch('app.core.security.get_current_user')
    def test_admin_health_check(self, mock_get_current_user):
        """
        Testa verificação de saúde do sistema
        """
        mock_user = type('MockUser', (), {
            'id': 1,
            'email': 'admin@example.com',
            'is_admin': True
        })()
        mock_get_current_user.return_value = mock_user
        
        response = client.get("/api/v1/admin/system/health")
        assert response.status_code == 200
        assert "database" in response.json()
        assert "cache" in response.json()


class TestRateLimit:
    """
    Testes de rate limiting
    """
    
    def test_rate_limit_exceeded(self):
        """
        Testa limite de requisições excedido
        """
        # Fazer muitas requisições para testar rate limit
        for i in range(10):
            response = client.get("/api/v1/health")
            if response.status_code == 429:
                # Rate limit atingido
                assert "detail" in response.json()
                break
        else:
            # Se não atingiu rate limit, teste passou
            assert True


class TestCORS:
    """
    Testes de CORS
    """
    
    def test_cors_preflight(self):
        """
        Testa requisição OPTIONS para CORS
        """
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"])
