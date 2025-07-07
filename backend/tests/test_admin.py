"""
Testes para endpoints de administração
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.usuario import Usuario, LogSistema, ConfiguracaoSistema
from app.core.security import security_service
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json

client = TestClient(app)


def create_test_user(db_session: Session, is_admin: bool = False):
    """Cria usuário para testes"""
    user = Usuario(
        username="testuser",
        email="test@example.com",
        nome_completo="Test User",
        senha_hash="$2b$12$1234567890123456789012",  # Hash fictício
        is_admin=is_admin,
        ativo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_test_logs(db_session: Session, user_id: int, count: int = 5):
    """Cria logs para testes"""
    logs = []
    for i in range(count):
        log = LogSistema(
            usuario_id=user_id,
            nivel="INFO" if i % 2 == 0 else "ERROR",
            categoria="TESTE",
            modulo="test_module",
            mensagem=f"Mensagem de teste {i}",
            created_at=datetime.now() - timedelta(hours=i)
        )
        db_session.add(log)
        logs.append(log)
    
    db_session.commit()
    return logs


def create_test_configuracoes(db_session: Session, count: int = 5):
    """Cria configurações para testes"""
    configuracoes = []
    categorias = ["SISTEMA", "API", "INTEGRACAO", "SEGURANCA", "NOTIFICACAO"]
    
    for i in range(count):
        config = ConfiguracaoSistema(
            chave=f"config_teste_{i}",
            valor=f"valor_{i}",
            tipo="STRING",
            descricao=f"Configuração de teste {i}",
            categoria=categorias[i % len(categorias)],
            ativo=True,
            somente_leitura=False
        )
        db_session.add(config)
        configuracoes.append(config)
    
    db_session.commit()
    return configuracoes


def get_admin_token(user_id: int):
    """Cria token de acesso para administrador"""
    return security_service.create_access_token(
        data={"sub": str(user_id), "is_admin": True},
        expires_delta=timedelta(minutes=30)
    )


def get_user_token(user_id: int):
    """Cria token de acesso para usuário comum"""
    return security_service.create_access_token(
        data={"sub": str(user_id), "is_admin": False},
        expires_delta=timedelta(minutes=30)
    )


class TestLogsEndpoints:
    def test_list_logs_as_admin(self, db_session: Session):
        """Testa listar logs como admin"""
        # Criar usuário admin
        user = create_test_user(db_session, is_admin=True)
        # Criar logs
        logs = create_test_logs(db_session, user.id, count=10)
        
        # Fazer requisição
        response = client.get(
            "/api/v1/admin/logs",
            headers={"Authorization": f"Bearer {get_admin_token(user.id)}"}
        )
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) > 0
        assert "total" in data
        assert data["total"] > 0
    
    def test_list_logs_with_filters(self, db_session: Session):
        """Testa listar logs com filtros"""
        # Criar usuário admin
        user = create_test_user(db_session, is_admin=True)
        # Criar logs
        logs = create_test_logs(db_session, user.id, count=10)
        
        # Fazer requisição com filtro
        response = client.get(
            "/api/v1/admin/logs?nivel=INFO",
            headers={"Authorization": f"Bearer {get_admin_token(user.id)}"}
        )
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert all(log["nivel"] == "INFO" for log in data["data"])
    
    def test_list_logs_forbidden_for_regular_user(self, db_session: Session):
        """Testa que usuário não-admin não pode listar logs"""
        # Criar usuário comum
        user = create_test_user(db_session, is_admin=False)
        
        # Fazer requisição
        response = client.get(
            "/api/v1/admin/logs",
            headers={"Authorization": f"Bearer {get_user_token(user.id)}"}
        )
        
        # Verificar resposta
        assert response.status_code == 403


class TestConfiguracoesEndpoints:
    def test_list_configuracoes_as_admin(self, db_session: Session):
        """Testa listar configurações como admin"""
        # Criar usuário admin
        user = create_test_user(db_session, is_admin=True)
        # Criar configurações
        configs = create_test_configuracoes(db_session, count=5)
        
        # Fazer requisição
        response = client.get(
            "/api/v1/admin/configuracoes",
            headers={"Authorization": f"Bearer {get_admin_token(user.id)}"}
        )
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_update_configuracao_as_admin(self, db_session: Session):
        """Testa atualizar configuração como admin"""
        # Criar usuário admin
        user = create_test_user(db_session, is_admin=True)
        # Criar configurações
        configs = create_test_configuracoes(db_session, count=1)
        
        # Configuração a ser atualizada
        config = configs[0]
        
        # Fazer requisição
        response = client.put(
            f"/api/v1/admin/configuracoes/{config.chave}?valor=novo_valor",
            headers={"Authorization": f"Bearer {get_admin_token(user.id)}"}
        )
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["valor"] == "novo_valor"
        
        # Verificar banco de dados
        db_session.refresh(config)
        assert config.valor == "novo_valor"
    
    def test_update_readonly_configuracao_forbidden(self, db_session: Session):
        """Testa que não é possível atualizar configuração somente leitura"""
        # Criar usuário admin
        user = create_test_user(db_session, is_admin=True)
        
        # Criar configuração somente leitura
        config = ConfiguracaoSistema(
            chave="config_somente_leitura",
            valor="valor_original",
            tipo="STRING",
            descricao="Configuração somente leitura",
            categoria="SISTEMA",
            ativo=True,
            somente_leitura=True
        )
        db_session.add(config)
        db_session.commit()
        
        # Fazer requisição
        response = client.put(
            f"/api/v1/admin/configuracoes/{config.chave}?valor=novo_valor",
            headers={"Authorization": f"Bearer {get_admin_token(user.id)}"}
        )
        
        # Verificar resposta
        assert response.status_code == 400
    
    def test_update_configuracao_forbidden_for_regular_user(self, db_session: Session):
        """Testa que usuário não-admin não pode atualizar configuração"""
        # Criar usuário comum
        user = create_test_user(db_session, is_admin=False)
        # Criar configurações
        configs = create_test_configuracoes(db_session, count=1)
        
        # Configuração a ser atualizada
        config = configs[0]
        
        # Fazer requisição
        response = client.put(
            f"/api/v1/admin/configuracoes/{config.chave}?valor=novo_valor",
            headers={"Authorization": f"Bearer {get_user_token(user.id)}"}
        )
        
        # Verificar resposta
        assert response.status_code == 403