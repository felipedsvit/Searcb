"""
Tests for user profile endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.usuario import Usuario
from app.core.security import security_service
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json

client = TestClient(app)


def create_test_user(db_session: Session, is_admin: bool = False):
    """Creates a test user"""
    user = Usuario(
        username="testuser",
        email="test@example.com",
        nome_completo="Test User",
        telefone="123456789",
        cargo="Analista",
        senha_hash="$2b$12$1234567890123456789012",  # Fake hash
        is_admin=is_admin,
        is_gestor=True,
        is_operador=True,
        ativo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestPerfilUsuario:
    """Tests for user profile endpoints"""

    def test_obter_perfil_atual(self, db_session: Session):
        """Test getting current user profile"""
        # Create test user
        user = create_test_user(db)
        
        # Create access token
        access_token = security_service.create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=30)
        )
        
        # Make request
        response = client.get(
            "/api/v1/usuarios/me/profile",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user.username
        assert data["email"] == user.email
        assert data["nome_completo"] == user.nome_completo
        assert data["telefone"] == user.telefone
        assert data["cargo"] == user.cargo
        assert data["is_admin"] == user.is_admin
        assert data["is_gestor"] == user.is_gestor
        assert data["is_operador"] == user.is_operador

    def test_atualizar_perfil_atual(self, db_session: Session):
        """Test updating current user profile"""
        # Create test user
        user = create_test_user(db)
        
        # Create access token
        access_token = security_service.create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=30)
        )
        
        # New profile data
        new_profile = {
            "nome_completo": "Updated Name",
            "telefone": "987654321",
            "cargo": "Gerente",
            "configuracoes": {"tema": "dark", "notificacoes": True}
        }
        
        # Make request
        response = client.put(
            "/api/v1/usuarios/me/profile",
            headers={"Authorization": f"Bearer {access_token}"},
            json=new_profile
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["nome_completo"] == new_profile["nome_completo"]
        assert data["telefone"] == new_profile["telefone"]
        assert data["cargo"] == new_profile["cargo"]
        assert data["configuracoes"] == new_profile["configuracoes"]
        
        # Verify database update
        updated_user = db_session.query(Usuario).filter(Usuario.id == user.id).first()
        assert updated_user.nome_completo == new_profile["nome_completo"]
        assert updated_user.telefone == new_profile["telefone"]
        assert updated_user.cargo == new_profile["cargo"]
        assert updated_user.configuracoes == new_profile["configuracoes"]

    def test_alterar_senha(self, db_session: Session):
        """Test changing user password"""
        # Create test user
        user = create_test_user(db)
        
        # Create access token
        access_token = security_service.create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=30)
        )
        
        # Password change request
        password_change = {
            "senha_atual": "current_password",  # In a real test, this would be the actual password
            "nova_senha": "new_secure_password"
        }
        
        # Mock the password verification
        with patch('app.core.security.verify_password', return_value=True):
            with patch('app.core.security.get_password_hash', return_value="new_hashed_password"):
                # Make request
                response = client.post(
                    f"/api/v1/usuarios/{user.id}/change-password",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=password_change
                )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Senha alterada com sucesso" in data["message"]
        
        # Verify database update (would check the hash in a real test)
        updated_user = db_session.query(Usuario).filter(Usuario.id == user.id).first()
        assert updated_user.senha_hash == "new_hashed_password"  # This would be the actual hash in a real test

    def test_alterar_senha_outro_usuario_nao_admin(self, db_session: Session):
        """Test that non-admin users cannot change others' passwords"""
        # Create test users
        user1 = create_test_user(db)
        user2 = create_test_user(db)
        user2.username = "testuser2"
        user2.email = "test2@example.com"
        db_session.add(user2)
        db_session.commit()
        
        # Create access token for user1
        access_token = security_service.create_access_token(
            data={"sub": user1.username},
            expires_delta=timedelta(minutes=30)
        )
        
        # Password change request for user2
        password_change = {
            "nova_senha": "new_secure_password"
        }
        
        # Make request to change user2's password
        response = client.post(
            f"/api/v1/usuarios/{user2.id}/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json=password_change
        )
        
        # Check response - should be forbidden
        assert response.status_code == 403
        assert "Sem permissão" in response.json()["detail"]

    def test_alterar_senha_admin(self, db_session: Session):
        """Test that admin users can change others' passwords"""
        # Create test users
        admin = create_test_user(db, is_admin=True)
        admin.username = "admin"
        admin.email = "admin@example.com"
        db_session.add(admin)
        db_session.commit()
        
        user = create_test_user(db)
        
        # Create access token for admin
        access_token = security_service.create_access_token(
            data={"sub": admin.username},
            expires_delta=timedelta(minutes=30)
        )
        
        # Password change request for user
        password_change = {
            "nova_senha": "admin_set_password"
        }
        
        # Mock the password hash function
        with patch('app.core.security.get_password_hash', return_value="admin_set_hash"):
            # Make request to change user's password
            response = client.post(
                f"/api/v1/usuarios/{user.id}/change-password",
                headers={"Authorization": f"Bearer {access_token}"},
                json=password_change
            )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Senha alterada com sucesso" in data["message"]
        
        # Verify database update
        updated_user = db_session.query(Usuario).filter(Usuario.id == user.id).first()
        assert updated_user.senha_hash == "admin_set_hash"  # This would be the actual hash in a real test
