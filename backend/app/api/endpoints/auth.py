from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from ...core.database import get_db
from ...core.security import security_service
from ...core.config import settings
from ...models.usuario import Usuario
from ...schemas.common import SuccessResponse, ErrorResponse
from ...schemas.usuario import UsuarioLogin, ChangePasswordRequest

logger = logging.getLogger(__name__)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


@router.post("/login", response_model=SuccessResponse)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint for user authentication using form data.
    
    **Parameters:**
    - **username**: Username or email (form field)
    - **password**: User password (form field)
    
    **Content-Type:** application/x-www-form-urlencoded
    
    **Returns:**
    - **access_token**: JWT access token
    - **token_type**: Token type (bearer)
    - **expires_in**: Token expiration time in seconds
    """
    return await _perform_login(form_data.username, form_data.password, db)


@router.post("/login-json", response_model=SuccessResponse)
async def login_json(
    login_data: UsuarioLogin,
    db: Session = Depends(get_db)
):
    """
    Login endpoint for user authentication using JSON data.
    
    **Parameters:**
    - **username**: Username or email (JSON field)
    - **password**: User password (JSON field)
    
    **Content-Type:** application/json
    
    **Returns:**
    - **access_token**: JWT access token
    - **token_type**: Token type (bearer)
    - **expires_in**: Token expiration time in seconds
    """
    return await _perform_login(login_data.username, login_data.password, db)


async def _perform_login(username: str, password: str, db: Session):
    """
    Perform user login with username/email and password.
    
    **Parameters:**
    - **username**: Username or email
    - **password**: User password
    
    **Returns:**
    - **access_token**: JWT access token
    - **token_type**: Token type (bearer)
    - **expires_in**: Token expiration time in seconds
    """
    try:
        # Find user by username or email
        user = db.query(Usuario).filter(
            (Usuario.username == username) | 
            (Usuario.email == username)
        ).first()
        
        if not user:
            logger.warning(f"Login attempt with invalid username: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not security_service.verify_password(password, user.senha_hash):
            logger.warning(f"Login attempt with invalid password for user: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.ativo:
            logger.warning(f"Login attempt for inactive user: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security_service.create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        # Update last login
        from datetime import datetime
        user.ultimo_login = datetime.utcnow()
        user.tentativas_login = 0
        db.commit()
        
        logger.info(f"Successful login for user: {user.username}")
        
        return {
            "success": True,
            "message": "Login realizado com sucesso",
            "timestamp": datetime.utcnow(),
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "nome_completo": user.nome_completo,
                    "is_admin": user.is_admin,
                    "is_gestor": user.is_gestor,
                    "is_operador": user.is_operador
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/logout", response_model=SuccessResponse)
async def logout(current_user: dict = Depends(security_service.get_current_user)):
    """
    Logout endpoint (invalidate token).
    
    **Note:** In a stateless JWT implementation, the client should simply discard the token.
    For a more secure implementation, consider maintaining a token blacklist.
    """
    logger.info(f"User logout: {current_user.get('username', 'unknown')}")
    
    return {
        "success": True,
        "message": "Logout realizado com sucesso",
        "timestamp": datetime.utcnow(),
        "data": None
    }


@router.get("/me", response_model=SuccessResponse)
async def get_current_user_info(
    current_user: dict = Depends(security_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information.
    
    **Returns:**
    - User profile information
    - User permissions
    - Organization information
    """
    try:
        user_id = current_user.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        return {
            "success": True,
            "message": "Informações do usuário obtidas com sucesso",
            "timestamp": datetime.utcnow(),
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "nome_completo": user.nome_completo,
                "cargo": user.cargo,
                "departamento": user.departamento,
                "telefone": user.telefone,
                "orgao_cnpj": user.orgao_cnpj,
                "orgao_nome": user.orgao_nome,
                "unidade_codigo": user.unidade_codigo,
                "unidade_nome": user.unidade_nome,
                "is_admin": user.is_admin,
                "is_gestor": user.is_gestor,
                "is_operador": user.is_operador,
                "ultimo_login": user.ultimo_login,
                "created_at": user.created_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/refresh", response_model=SuccessResponse)
async def refresh_token(
    current_user: dict = Depends(security_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Refresh access token.
    
    **Returns:**
    - New access token
    - Token expiration time
    """
    try:
        user_id = current_user.get("sub")
        username = current_user.get("username")
        
        # Verify user still exists and is active
        user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
        if not user or not user.ativo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inválido ou inativo"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security_service.create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Token refreshed for user: {username}")
        
        return {
            "success": True,
            "message": "Token renovado com sucesso",
            "timestamp": datetime.utcnow(),
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(security_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    
    **Parameters:**
    - **senha_atual**: Current password
    - **senha_nova**: New password
    - **confirmar_senha_nova**: New password confirmation
    
    **Returns:**
    - Success message
    """
    try:
        user_id = current_user.get("sub")
        user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verify old password
        if not security_service.verify_password(password_data.senha_atual, user.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )
        
        # Update password (validation is already done by Pydantic)
        user.senha_hash = security_service.get_password_hash(password_data.senha_nova)
        user.data_expiracao_senha = None  # Reset password expiration
        db.commit()
        
        logger.info(f"Password changed for user: {user.username}")
        
        return {
            "success": True,
            "message": "Senha alterada com sucesso",
            "timestamp": datetime.utcnow(),
            "data": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/validate", response_model=SuccessResponse)
async def validate_token(current_user: dict = Depends(security_service.get_current_user)):
    """
    Validate access token.
    
    **Returns:**
    - Token validation status
    - User basic information
    """
    return {
        "success": True,
        "message": "Token válido",
        "data": {
            "user_id": current_user.get("sub"),
            "username": current_user.get("username"),
            "valid": True
        }
    }
