from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import DbSession
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import Usuario
from app.modules.estadisticas.schemas import (
    EstadisticasResumen,
    EstadisticasVentasDia,
    EstadisticasProductoTop,
    EstadisticasPedidosEstado,
    EstadisticasIngresosFormaPago
)
from app.modules.estadisticas.service import EstadisticasService

router = APIRouter()

def get_estadisticas_service(session: DbSession) -> EstadisticasService:
    return EstadisticasService(session)

@router.get("/resumen", response_model=EstadisticasResumen)
def get_resumen(
    _current_user: Annotated[Usuario, Depends(require_permission("estadisticas", "read"))],
    svc: EstadisticasService = Depends(get_estadisticas_service),
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
) -> EstadisticasResumen:
    return svc.get_resumen(desde, hasta)

@router.get("/ventas", response_model=list[EstadisticasVentasDia])
def get_ventas_por_dia(
    _current_user: Annotated[Usuario, Depends(require_permission("estadisticas", "read"))],
    svc: EstadisticasService = Depends(get_estadisticas_service),
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
) -> list[EstadisticasVentasDia]:
    return svc.get_ventas_por_dia(desde, hasta)

@router.get("/productos-top", response_model=list[EstadisticasProductoTop])
def get_productos_top(
    _current_user: Annotated[Usuario, Depends(require_permission("estadisticas", "read"))],
    svc: EstadisticasService = Depends(get_estadisticas_service),
    limite: int = Query(5, ge=1, le=20),
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
) -> list[EstadisticasProductoTop]:
    return svc.get_productos_top(limite, desde, hasta)

@router.get("/pedidos-por-estado", response_model=list[EstadisticasPedidosEstado])
def get_pedidos_por_estado(
    _current_user: Annotated[Usuario, Depends(require_permission("estadisticas", "read"))],
    svc: EstadisticasService = Depends(get_estadisticas_service),
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
) -> list[EstadisticasPedidosEstado]:
    return svc.get_pedidos_por_estado(desde, hasta)

@router.get("/ingresos", response_model=list[EstadisticasIngresosFormaPago])
def get_ingresos_por_forma_pago(
    _current_user: Annotated[Usuario, Depends(require_permission("estadisticas", "read"))],
    svc: EstadisticasService = Depends(get_estadisticas_service),
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
) -> list[EstadisticasIngresosFormaPago]:
    return svc.get_ingresos_por_forma_pago(desde, hasta)
