from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.router import router as auth_router
from app.modules.categoria.router import router as categoria_router
from app.modules.ingrediente.router import router as ingrediente_router
from app.modules.producto.router import router as producto_router

api_router = APIRouter()

protected_route_dependencies = [Depends(get_current_active_user)]

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(
    categoria_router,
    prefix="/categorias",
    tags=["categorias"],
    dependencies=protected_route_dependencies,
)
api_router.include_router(
    producto_router,
    prefix="/productos",
    tags=["productos"],
    dependencies=protected_route_dependencies,
)
api_router.include_router(
    ingrediente_router,
    prefix="/ingredientes",
    tags=["ingredientes"],
    dependencies=protected_route_dependencies,
)
