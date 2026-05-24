from fastapi import APIRouter

from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.categoria.router import router as categoria_router
from app.modules.direcciones.router import router as direcciones_router
from app.modules.ingrediente.router import router as ingrediente_router
from app.modules.pedidos.router import router as pedidos_router
from app.modules.producto.router import router as producto_router
from app.modules.ventas.router import router as ventas_router

api_router = APIRouter()

api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(
    categoria_router,
    prefix="/categorias",
    tags=["categorias"],
)
api_router.include_router(
    producto_router,
    prefix="/productos",
    tags=["productos"],
)
api_router.include_router(
    ingrediente_router,
    prefix="/ingredientes",
    tags=["ingredientes"],
)
api_router.include_router(
    direcciones_router,
    prefix="/direcciones",
    tags=["direcciones"],
)
api_router.include_router(
    pedidos_router,
    prefix="/pedidos",
    tags=["pedidos"],
)
api_router.include_router(
    ventas_router,
    prefix="/ventas",
    tags=["ventas"],
)
