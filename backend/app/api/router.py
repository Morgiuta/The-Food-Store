from fastapi import APIRouter

from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.categoria.router import router as categoria_router
from app.modules.direcciones.router import router as direcciones_router
from app.modules.ingrediente.router import router as ingrediente_router
from app.modules.pagos.router import router as pagos_router
from app.modules.pedidos.router import router as pedidos_router
from app.modules.producto.router import router as producto_router
from app.modules.unidad_medida.router import router as unidad_medida_router
from app.modules.ventas.router import router as ventas_router
from app.modules.estadisticas.router import router as estadisticas_router

api_router = APIRouter()

api_router.include_router(
    estadisticas_router,
    prefix="/estadisticas",
    tags=["estadisticas"],
)

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
    unidad_medida_router,
    prefix="/unidades-medida",
    tags=["unidades-medida"],
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
api_router.include_router(
    pagos_router,
    prefix="/pagos",
    tags=["pagos"],
)
from app.modules.uploads.router import router as uploads_router
api_router.include_router(
    uploads_router,
    tags=["uploads"],
)
