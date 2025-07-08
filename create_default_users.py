#!/usr/bin/env python3
"""
Script para criar usuários padrão no banco de dados
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.usuario import Usuario
from app.core.security import security_service
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_default_users():
    """Create default users for testing"""
    try:
        # Create database connection
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if users already exist
        existing_admin = db.query(Usuario).filter(Usuario.username == "admin").first()
        existing_user = db.query(Usuario).filter(Usuario.username == "user").first()
        
        if not existing_admin:
            # Create admin user
            admin = Usuario(
                username="admin",
                email="admin@searcb.gov.br",
                nome_completo="Administrador do Sistema",
                telefone="11999999999",
                cargo="Administrador",
                orgao_cnpj="00000000000000",
                orgao_nome="Órgão Teste",
                senha_hash=security_service.get_password_hash("admin"),
                is_admin=True,
                is_gestor=True,
                is_operador=True,
                ativo=True
            )
            db.add(admin)
            logger.info("Created admin user")
        else:
            logger.info("Admin user already exists")
        
        if not existing_user:
            # Create regular user
            user = Usuario(
                username="user",
                email="user@searcb.gov.br",
                nome_completo="Usuário Teste",
                telefone="11888888888",
                cargo="Analista",
                orgao_cnpj="00000000000001",
                orgao_nome="Órgão Teste Usuário",
                senha_hash=security_service.get_password_hash("password"),
                is_admin=False,
                is_gestor=False,
                is_operador=True,
                ativo=True
            )
            db.add(user)
            logger.info("Created regular user")
        else:
            logger.info("Regular user already exists")
        
        db.commit()
        logger.info("Default users created successfully")
        
        # Verify users were created
        admin_check = db.query(Usuario).filter(Usuario.username == "admin").first()
        user_check = db.query(Usuario).filter(Usuario.username == "user").first()
        
        if admin_check and user_check:
            logger.info(f"Verification successful - Admin ID: {admin_check.id}, User ID: {user_check.id}")
        else:
            logger.error("Verification failed - Users not found")
            
    except Exception as e:
        logger.error(f"Error creating default users: {e}")
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    create_default_users()
