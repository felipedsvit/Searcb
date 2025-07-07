"""
Testes unitários para serviços
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.services.pncp_service import PNCPService
from app.services.usuario_service import UsuarioService
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate
from app.core.security import SecurityService


class TestPNCPService:
    """
    Testes para o serviço PNCP
    """
    
    def setup_method(self):
        """Setup para cada teste"""
        self.pncp_service = PNCPService()
    
    @pytest.mark.asyncio
    async def test_obter_pcas_success(self):
        """
        Testa obtenção de PCAs com sucesso
        """
        # Mock da resposta da API
        mock_response = {
            "data": [
                {
                    "id": "123",
                    "ano": 2024,
                    "orgao_cnpj": "12345678000100",
                    "orgao_nome": "Prefeitura Municipal",
                    "valor_total": 1000000.00
                }
            ],
            "total": 1,
            "page": 1,
            "size": 20
        }
        
        with patch.object(self.pncp_service, '_make_request', return_value=mock_response):
            with patch('app.services.pncp_service.get_cache', return_value=None):
                with patch('app.services.pncp_service.set_cache', return_value=None):
                    result = await self.pncp_service.obter_pcas(
                        cnpj_orgao="12345678000100",
                        ano=2024,
                        pagina=1,
                        tamanho=20
                    )
                    
                    assert result == mock_response
                    assert len(result["data"]) == 1
                    assert result["data"][0]["ano"] == 2024
    
    @pytest.mark.asyncio
    async def test_obter_pcas_from_cache(self):
        """
        Testa obtenção de PCAs do cache
        """
        cached_response = {
            "data": [{"id": "123", "ano": 2024}],
            "total": 1
        }
        
        with patch('app.services.pncp_service.get_cache', return_value=cached_response):
            result = await self.pncp_service.obter_pcas()
            
            assert result == cached_response
    
    @pytest.mark.asyncio
    async def test_obter_pca_por_id_success(self):
        """
        Testa obtenção de PCA por ID
        """
        mock_response = {
            "id": "123",
            "ano": 2024,
            "orgao_cnpj": "12345678000100",
            "status": "ATIVO"
        }
        
        with patch.object(self.pncp_service, '_make_request', return_value=mock_response):
            with patch('app.services.pncp_service.get_cache', return_value=None):
                with patch('app.services.pncp_service.set_cache', return_value=None):
                    result = await self.pncp_service.obter_pca_por_id("123")
                    
                    assert result == mock_response
                    assert result["id"] == "123"
                    assert result["ano"] == 2024
    
    @pytest.mark.asyncio
    async def test_sincronizar_dados_success(self):
        """
        Testa sincronização de dados com sucesso
        """
        mock_pcas = {"data": [{"id": "1"}, {"id": "2"}]}
        mock_contratacoes = {"data": [{"id": "1"}]}
        mock_atas = {"data": [{"id": "1"}]}
        mock_contratos = {"data": [{"id": "1"}]}
        
        with patch.object(self.pncp_service, 'obter_pcas', return_value=mock_pcas):
            with patch.object(self.pncp_service, 'obter_contratacoes', return_value=mock_contratacoes):
                with patch.object(self.pncp_service, 'obter_atas', return_value=mock_atas):
                    with patch.object(self.pncp_service, 'obter_contratos', return_value=mock_contratos):
                        result = await self.pncp_service.sincronizar_dados(
                            data_inicio=date(2024, 1, 1),
                            data_fim=date(2024, 12, 31)
                        )
                        
                        assert result["pcas"] == 2
                        assert result["contratacoes"] == 1
                        assert result["atas"] == 1
                        assert result["contratos"] == 1
                        assert len(result["erros"]) == 0


class TestUsuarioService:
    """
    Testes para o serviço de usuários
    """
    
    def setup_method(self):
        """Setup para cada teste"""
        self.db = Mock(spec=Session)
        self.usuario_service = UsuarioService(self.db)
    
    @pytest.mark.asyncio
    async def test_create_usuario_success(self):
        """
        Testa criação de usuário com sucesso
        """
        usuario_data = UsuarioCreate(
            username="testuser",
            email="test@example.com",
            nome_completo="Test User",
            senha="password123",
            confirmar_senha="password123"
        )
        
        # Mock para verificar se usuário já existe
        self.db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock para criar usuário
        mock_usuario = Usuario(
            id=1,
            username="testuser",
            email="test@example.com",
            nome_completo="Test User",
            senha_hash="hashed_password"
        )
        
        with patch('app.services.usuario_service.get_cache', return_value=None):
            with patch('app.services.usuario_service.delete_cache', return_value=None):
                with patch('app.services.usuario_service.security_service.get_password_hash', return_value="hashed_password"):
                    self.db.add.return_value = None
                    self.db.commit.return_value = None
                    self.db.refresh.return_value = None
                    
                    result = await self.usuario_service.create_usuario(usuario_data)
                    
                    assert self.db.add.called
                    assert self.db.commit.called
                    assert self.db.refresh.called
    
    @pytest.mark.asyncio
    async def test_create_usuario_duplicate_username(self):
        """
        Testa criação de usuário com username duplicado
        """
        usuario_data = UsuarioCreate(
            username="testuser",
            email="test@example.com",
            nome_completo="Test User",
            senha="password123",
            confirmar_senha="password123"
        )
        
        # Mock para usuário existente
        existing_user = Usuario(username="testuser")
        
        with patch.object(self.usuario_service, 'get_usuario_by_username', return_value=existing_user):
            with pytest.raises(Exception) as exc_info:
                await self.usuario_service.create_usuario(usuario_data)
            
            assert "Username já cadastrado" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_authenticate_usuario_success(self):
        """
        Testa autenticação de usuário com sucesso
        """
        # Mock do usuário
        mock_usuario = Usuario(
            id=1,
            username="testuser",
            email="test@example.com",
            senha_hash="hashed_password",
            ativo=True,
            tentativas_login=0
        )
        
        self.db.query.return_value.filter.return_value.first.return_value = mock_usuario
        
        with patch('app.services.usuario_service.security_service.verify_password', return_value=True):
            result = await self.usuario_service.authenticate_usuario("testuser", "password123")
            
            assert result == mock_usuario
            assert mock_usuario.tentativas_login == 0
            assert mock_usuario.ultimo_login is not None
    
    @pytest.mark.asyncio
    async def test_authenticate_usuario_invalid_password(self):
        """
        Testa autenticação com senha inválida
        """
        # Mock do usuário
        mock_usuario = Usuario(
            id=1,
            username="testuser",
            email="test@example.com",
            senha_hash="hashed_password",
            ativo=True,
            tentativas_login=0
        )
        
        self.db.query.return_value.filter.return_value.first.return_value = mock_usuario
        
        with patch('app.services.usuario_service.security_service.verify_password', return_value=False):
            result = await self.usuario_service.authenticate_usuario("testuser", "wrongpassword")
            
            assert result is None
            assert mock_usuario.tentativas_login == 1
    
    @pytest.mark.asyncio
    async def test_authenticate_usuario_not_found(self):
        """
        Testa autenticação com usuário não encontrado
        """
        self.db.query.return_value.filter.return_value.first.return_value = None
        
        result = await self.usuario_service.authenticate_usuario("nonexistent", "password123")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_usuario_by_id_from_cache(self):
        """
        Testa obtenção de usuário por ID do cache
        """
        cached_usuario = Usuario(id=1, username="testuser")
        
        with patch('app.services.usuario_service.get_cache', return_value=cached_usuario):
            result = await self.usuario_service.get_usuario_by_id(1)
            
            assert result == cached_usuario
    
    @pytest.mark.asyncio
    async def test_get_usuario_by_id_from_db(self):
        """
        Testa obtenção de usuário por ID do banco
        """
        mock_usuario = Usuario(id=1, username="testuser")
        
        self.db.query.return_value.filter.return_value.first.return_value = mock_usuario
        
        with patch('app.services.usuario_service.get_cache', return_value=None):
            with patch('app.services.usuario_service.set_cache', return_value=None):
                result = await self.usuario_service.get_usuario_by_id(1)
                
                assert result == mock_usuario
    
    @pytest.mark.asyncio
    async def test_list_usuarios_with_filters(self):
        """
        Testa listagem de usuários com filtros
        """
        mock_usuarios = [
            Usuario(id=1, username="user1"),
            Usuario(id=2, username="user2")
        ]
        
        # Mock da query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_usuarios
        
        self.db.query.return_value = mock_query
        
        result = await self.usuario_service.list_usuarios(
            skip=0,
            limit=10,
            search="user",
            ativo=True
        )
        
        assert result == mock_usuarios
        assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_update_usuario_success(self):
        """
        Testa atualização de usuário com sucesso
        """
        mock_usuario = Usuario(
            id=1,
            username="testuser",
            email="test@example.com",
            nome_completo="Test User"
        )
        
        update_data = Mock()
        update_data.dict.return_value = {
            "nome_completo": "Updated User",
            "email": "updated@example.com"
        }
        update_data.email = "updated@example.com"
        
        with patch.object(self.usuario_service, 'get_usuario_by_id', return_value=mock_usuario):
            with patch.object(self.usuario_service, 'get_usuario_by_email', return_value=None):
                with patch('app.services.usuario_service.delete_cache', return_value=None):
                    result = await self.usuario_service.update_usuario(1, update_data)
                    
                    assert mock_usuario.nome_completo == "Updated User"
                    assert mock_usuario.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_delete_usuario_success(self):
        """
        Testa remoção de usuário com sucesso
        """
        mock_usuario = Usuario(id=1, username="testuser")
        mock_usuario.soft_delete = Mock()
        
        with patch.object(self.usuario_service, 'get_usuario_by_id', return_value=mock_usuario):
            with patch('app.services.usuario_service.delete_cache', return_value=None):
                result = await self.usuario_service.delete_usuario(1)
                
                assert result is True
                assert mock_usuario.soft_delete.called
                assert self.db.commit.called


class TestSecurityService:
    """
    Testes para o serviço de segurança
    """
    
    def setup_method(self):
        """Setup para cada teste"""
        self.security_service = SecurityService()
    
    def test_get_password_hash(self):
        """
        Testa geração de hash de senha
        """
        password = "testpassword123"
        hash_result = self.security_service.get_password_hash(password)
        
        assert hash_result is not None
        assert hash_result != password
        assert len(hash_result) > 0
    
    def test_verify_password_success(self):
        """
        Testa verificação de senha com sucesso
        """
        password = "testpassword123"
        hash_result = self.security_service.get_password_hash(password)
        
        is_valid = self.security_service.verify_password(password, hash_result)
        
        assert is_valid is True
    
    def test_verify_password_failure(self):
        """
        Testa verificação de senha com falha
        """
        password = "testpassword123"
        wrong_password = "wrongpassword123"
        hash_result = self.security_service.get_password_hash(password)
        
        is_valid = self.security_service.verify_password(wrong_password, hash_result)
        
        assert is_valid is False
    
    def test_create_access_token(self):
        """
        Testa criação de token de acesso
        """
        data = {"sub": "testuser", "user_id": 1}
        token = self.security_service.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_access_token(self):
        """
        Testa decodificação de token de acesso
        """
        data = {"sub": "testuser", "user_id": 1}
        token = self.security_service.create_access_token(data)
        
        decoded_data = self.security_service.decode_access_token(token)
        
        assert decoded_data is not None
        assert decoded_data["sub"] == "testuser"
        assert decoded_data["user_id"] == 1
    
    def test_decode_invalid_token(self):
        """
        Testa decodificação de token inválido
        """
        invalid_token = "invalid.token.here"
        
        decoded_data = self.security_service.decode_access_token(invalid_token)
        
        assert decoded_data is None
