from fastapi import APIRouter

from app.modules.categoria.router import router as categoria_router
from app.modules.ingrediente.router import router as ingrediente_router
from app.modules.producto.router import router as producto_router
from app.modules.producto_categoria.router import router as producto_categoria_router
from app.modules.producto_ingrediente.router import router as producto_ingrediente_router

api_router = APIRouter()

api_router.include_router(categoria_router, prefix="/categorias", tags=["categorias"])
api_router.include_router(producto_router, prefix="/productos", tags=["productos"])
api_router.include_router(ingrediente_router, prefix="/ingredientes", tags=["ingredientes"])
api_router.include_router(
    producto_categoria_router,
    prefix="/producto-categorias",
    tags=["producto-categorias"],
)
api_router.include_router(
    producto_ingrediente_router,
    prefix="/producto-ingredientes",
    tags=["producto-ingredientes"],
)
