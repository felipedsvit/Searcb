from fastapi import APIRouter

from .endpoints import auth, pca, contratacao, ata, contrato, webhooks, admin, usuarios

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(pca.router, prefix="/pca", tags=["PCA - Planos Anuais de Contratação"])
api_router.include_router(contratacao.router, prefix="/contratacoes", tags=["Contratações"])
api_router.include_router(ata.router, prefix="/atas", tags=["Atas de Registro de Preços"])
api_router.include_router(contrato.router, prefix="/contratos", tags=["Contratos"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administração"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuários"])
