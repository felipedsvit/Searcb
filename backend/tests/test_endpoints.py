"""
Test script for validating the newly implemented endpoints
"""
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import json

# Ensure the app directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock database and dependencies
from app.core.database import Base, get_db
from app.core.security import get_current_user, security_service
from app.models.usuario import Usuario, LogSistema, ConfiguracaoSistema
from app.api.endpoints import admin, webhooks, usuarios


class MockDB:
    def __init__(self):
        self.items = {}
        self.commited = False
        
    def query(self, model):
        return MockQuery(self, model)
    
    def add(self, item):
        if not hasattr(item, 'id'):
            item.id = len(self.items.get(item.__class__, [])) + 1
        
        if item.__class__ not in self.items:
            self.items[item.__class__] = []
        
        self.items[item.__class__].append(item)
    
    def commit(self):
        self.commited = True
    
    def rollback(self):
        pass
    
    def refresh(self, item):
        pass


class MockQuery:
    def __init__(self, db, model):
        self.db = db
        self.model = model
        self.filters = []
        self.order_columns = []
        self.limit_val = None
        self.offset_val = None
    
    def filter(self, *args):
        self.filters.extend(args)
        return self
    
    def order_by(self, *args):
        self.order_columns.extend(args)
        return self
    
    def offset(self, offset):
        self.offset_val = offset
        return self
    
    def limit(self, limit):
        self.limit_val = limit
        return self
    
    def all(self):
        items = self.db.items.get(self.model, [])
        # Would apply filters, order, offset, limit here in a real implementation
        return items
    
    def count(self):
        return len(self.db.items.get(self.model, []))
    
    def first(self):
        items = self.db.items.get(self.model, [])
        return items[0] if items else None


class TestAdminEndpoints(unittest.TestCase):
    def setUp(self):
        self.db = MockDB()
        
        # Create admin user
        self.admin = Usuario(
            id=1,
            username="admin",
            email="admin@example.com",
            nome_completo="Admin User",
            senha_hash="hashed_password",
            is_admin=True,
            ativo=True,
            created_at=datetime.now()
        )
        self.db.add(self.admin)
        
        # Create logs
        for i in range(5):
            log = LogSistema(
                nivel="INFO" if i % 2 == 0 else "ERROR",
                categoria="TEST",
                modulo="test_module",
                mensagem=f"Test message {i}",
                created_at=datetime.now() - timedelta(hours=i),
                updated_at=datetime.now()
            )
            self.db.add(log)
        
        # Create configurations
        configs = [
            ("pncp_sync_interval", "3600", "Intervalo de sincronização com PNCP (segundos)", "integracao", "INTEGER"),
            ("max_page_size", "500", "Tamanho máximo de página para consultas", "api", "INTEGER"),
            ("cache_ttl", "3600", "Tempo de vida do cache (segundos)", "cache", "INTEGER"),
            ("rate_limit_requests", "100", "Limite de requisições por minuto", "seguranca", "INTEGER"),
            ("email_notifications", "true", "Habilitar notificações por email", "notificacoes", "BOOLEAN")
        ]
        
        for i, (chave, valor, descricao, categoria, tipo) in enumerate(configs):
            config = ConfiguracaoSistema(
                id=i+1,
                chave=chave,
                valor=valor,
                descricao=descricao,
                categoria=categoria,
                tipo=tipo,
                ativo=True,
                somente_leitura=False,
                valor_padrao=valor,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.db.add(config)
    
    @patch('app.api.endpoints.admin.get_db')
    @patch('app.api.endpoints.admin.get_current_user')
    async def test_listar_logs(self, mock_get_current_user, mock_get_db):
        # Mock dependencies
        mock_get_db.return_value = self.db
        mock_get_current_user.return_value = self.admin
        
        # Create mock request
        request = MagicMock()
        
        # Call the endpoint
        response = await admin.listar_logs(
            request=request,
            page=1,
            size=10,
            nivel=None,
            modulo=None,
            categoria=None,
            data_inicio=None,
            data_fim=None,
            termo_busca=None,
            usuario_id=None,
            current_user=self.admin,
            db=self.db
        )
        
        # Assertions
        self.assertIsNotNone(response)
        self.assertIn("data", response)
        self.assertEqual(len(response["data"]), 5)
        self.assertEqual(response["total"], 5)
        self.assertEqual(response["page"], 1)
        self.assertEqual(response["size"], 10)
    
    @patch('app.api.endpoints.admin.get_db')
    @patch('app.api.endpoints.admin.get_current_user')
    @patch('app.api.endpoints.admin.get_cache')
    @patch('app.api.endpoints.admin.set_cache')
    async def test_listar_configuracoes(self, mock_set_cache, mock_get_cache, mock_get_current_user, mock_get_db):
        # Mock dependencies
        mock_get_db.return_value = self.db
        mock_get_current_user.return_value = self.admin
        mock_get_cache.return_value = None
        mock_set_cache.return_value = True
        
        # Create mock request
        request = MagicMock()
        
        # Call the endpoint
        response = await admin.listar_configuracoes(
            request=request,
            categoria=None,
            ativo=None,
            page=1,
            size=10,
            current_user=self.admin,
            db=self.db
        )
        
        # Assertions
        self.assertIsNotNone(response)
        self.assertIn("data", response)
        self.assertGreater(len(response["data"]), 0)
    
    @patch('app.api.endpoints.admin.get_db')
    @patch('app.api.endpoints.admin.get_current_user')
    @patch('app.api.endpoints.admin.clear_cache_pattern')
    async def test_atualizar_configuracao(self, mock_clear_cache, mock_get_current_user, mock_get_db):
        # Mock dependencies
        mock_get_db.return_value = self.db
        mock_get_current_user.return_value = self.admin
        mock_clear_cache.return_value = True
        
        # Call the endpoint
        response = await admin.atualizar_configuracao(
            chave="max_page_size",
            valor="1000",
            current_user=self.admin,
            db=self.db
        )
        
        # Assertions
        self.assertIsNotNone(response)
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["chave"], "max_page_size")
        self.assertEqual(response["valor"], "1000")


class TestWebhookEndpoints(unittest.TestCase):
    def setUp(self):
        self.db = MockDB()
        
        # Create admin user
        self.admin = Usuario(
            id=1,
            username="admin",
            email="admin@example.com",
            nome_completo="Admin User",
            senha_hash="hashed_password",
            is_admin=True,
            ativo=True,
            created_at=datetime.now()
        )
        self.db.add(self.admin)
    
    @patch('app.api.endpoints.webhooks.get_db')
    @patch('app.api.endpoints.webhooks.get_current_user')
    async def test_receber_notificacao_interna(self, mock_get_current_user, mock_get_db):
        # Mock dependencies
        mock_get_db.return_value = self.db
        mock_get_current_user.return_value = self.admin
        
        # Create mock request
        request = MagicMock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}
        
        # Payload for the webhook
        payload = {
            "tipo": "contrato_vencendo",
            "dados": {
                "contrato_id": 1,
                "dias_vencimento": 30
            },
            "origem": "test",
            "prioridade": "alta"
        }
        
        # Call the endpoint
        response = await webhooks.receber_notificacao_interna(
            request=request,
            payload=payload,
            db=self.db,
            current_user=self.admin
        )
        
        # Assertions
        self.assertIsNotNone(response)
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["tipo"], "contrato_vencendo")
        self.assertIn("timestamp", response)


class TestUsuarioEndpoints(unittest.TestCase):
    def setUp(self):
        self.db = MockDB()
        
        # Create regular user
        self.user = Usuario(
            id=1,
            username="user",
            email="user@example.com",
            nome_completo="Regular User",
            senha_hash="hashed_password",
            telefone="1234567890",
            cargo="Analista",
            departamento="TI",
            orgao_cnpj="12345678901234",
            orgao_nome="Organização Teste",
            unidade_codigo="001",
            unidade_nome="Unidade Teste",
            is_admin=False,
            is_gestor=False,
            is_operador=True,
            ativo=True,
            ultimo_login=datetime.now() - timedelta(days=1),
            created_at=datetime.now() - timedelta(days=30),
            updated_at=datetime.now() - timedelta(days=10)
        )
        self.db.add(self.user)
    
    @patch('app.api.endpoints.usuarios.get_db')
    @patch('app.api.endpoints.usuarios.get_current_user')
    async def test_obter_perfil_atual(self, mock_get_current_user, mock_get_db):
        # Mock dependencies
        mock_get_db.return_value = self.db
        mock_get_current_user.return_value = self.user
        
        # Create mock request
        request = None
        
        # Call the endpoint
        response = await usuarios.obter_perfil_atual(
            request=request,
            current_user=self.user,
            db=self.db
        )
        
        # Assertions
        self.assertIsNotNone(response)
        self.assertEqual(response["id"], 1)
        self.assertEqual(response["username"], "user")
        self.assertEqual(response["email"], "user@example.com")
        self.assertEqual(response["nome_completo"], "Regular User")
        self.assertEqual(response["telefone"], "1234567890")
        self.assertEqual(response["cargo"], "Analista")
        self.assertEqual(response["departamento"], "TI")
    
    @patch('app.api.endpoints.usuarios.get_db')
    @patch('app.api.endpoints.usuarios.get_current_user')
    async def test_atualizar_perfil_atual(self, mock_get_current_user, mock_get_db):
        # Mock dependencies
        mock_get_db.return_value = self.db
        mock_get_current_user.return_value = self.user
        
        # Create mock request
        request = None
        
        # Call the endpoint
        response = await usuarios.atualizar_perfil_atual(
            request=request,
            nome_completo="Usuário Atualizado",
            telefone="9876543210",
            cargo="Coordenador",
            departamento="Recursos Humanos",
            current_user=self.user,
            db=self.db
        )
        
        # Assertions
        self.assertIsNotNone(response)
        self.assertEqual(response["nome_completo"], "Usuário Atualizado")
        self.assertEqual(response["telefone"], "9876543210")
        self.assertEqual(response["cargo"], "Coordenador")
        self.assertEqual(response["departamento"], "Recursos Humanos")
    
    @patch('app.api.endpoints.usuarios.get_db')
    @patch('app.api.endpoints.usuarios.get_current_user')
    async def test_alterar_senha_usuario(self, mock_get_current_user, mock_get_db):
        # Mock dependencies
        mock_get_db.return_value = self.db
        mock_get_current_user.return_value = self.user
        
        # Mock security service
        from app.core.security import SecurityService
        security_service_mock = MagicMock()
        security_service_mock.verify_password.return_value = True
        security_service_mock.get_password_hash.return_value = "new_hashed_password"
        
        # Patch the security service
        with patch('app.api.endpoints.usuarios.SecurityService', return_value=security_service_mock):
            # Call the endpoint
            response = await usuarios.alterar_senha_usuario(
                usuario_id=1,
                senha_atual="old_password",
                nova_senha="new_password",
                current_user=self.user,
                db=self.db
            )
            
            # Assertions
            self.assertIsNotNone(response)
            self.assertEqual(response["status"], "success")
            self.assertEqual(response["message"], "Senha alterada com sucesso")


if __name__ == "__main__":
    unittest.main()
