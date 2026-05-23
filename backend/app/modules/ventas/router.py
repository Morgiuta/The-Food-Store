from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import DbSession
from app.modules.auth.dependencies import get_current_active_user, require_permission
from app.modules.auth.models import Usuario
from app.modules.ventas.schemas import (
    EstadoPedidoPublic,
    FormaPagoPublic,
    PagoCreate,
    PagoPublic,
    PedidoCreate,
    PedidoEstadoUpdate,
    PedidoList,
    PedidoPublic,
)
from app.modules.ventas.service import VentasService

router = APIRouter()


def get_ventas_service(session: DbSession) -> VentasService:
    return VentasService(session)


@router.get("/formas-pago", response_model=list[FormaPagoPublic])
def list_formas_pago(
    _current_user=Depends(require_permission("pedido", "read")),
    svc: VentasService = Depends(get_ventas_service),
) -> list[FormaPagoPublic]:
    return svc.list_formas_pago()


@router.get("/estados", response_model=list[EstadoPedidoPublic])
def list_estados(
    _current_user=Depends(require_permission("pedido", "read")),
    svc: VentasService = Depends(get_ventas_service),
) -> list[EstadoPedidoPublic]:
    return svc.list_estados()


@router.post("/pedidos", response_model=PedidoPublic, status_code=status.HTTP_201_CREATED)
def create_pedido(
    data: PedidoCreate,
    current_user: Annotated[Usuario, Depends(get_current_active_user)],
    svc: VentasService = Depends(get_ventas_service),
) -> PedidoPublic:
    return svc.create_pedido(current_user.id or 0, data)


@router.get("/pedidos", response_model=PedidoList)
def list_pedidos(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    _current_user=Depends(require_permission("pedido", "read")),
    svc: VentasService = Depends(get_ventas_service),
) -> PedidoList:
    return svc.list_pedidos(offset=offset, limit=limit)


@router.get("/pedidos/{pedido_id}", response_model=PedidoPublic)
def get_pedido(
    pedido_id: Annotated[int, Path(gt=0)],
    _current_user=Depends(require_permission("pedido", "read")),
    svc: VentasService = Depends(get_ventas_service),
) -> PedidoPublic:
    return svc.get_pedido(pedido_id)


@router.post("/pedidos/{pedido_id}/estado", response_model=PedidoPublic)
def change_estado(
    pedido_id: Annotated[int, Path(gt=0)],
    data: PedidoEstadoUpdate,
    current_user: Annotated[Usuario, Depends(require_permission("pedido", "update"))],
    svc: VentasService = Depends(get_ventas_service),
) -> PedidoPublic:
    return svc.change_estado(
        pedido_id=pedido_id,
        estado_hacia=data.estado_hacia,
        usuario_id=current_user.id,
        motivo=data.motivo,
    )


@router.post(
    "/pedidos/{pedido_id}/pagos",
    response_model=PagoPublic,
    status_code=status.HTTP_201_CREATED,
)
def register_pago(
    pedido_id: Annotated[int, Path(gt=0)],
    data: PagoCreate,
    _current_user=Depends(require_permission("pedido", "update")),
    svc: VentasService = Depends(get_ventas_service),
) -> PagoPublic:
    return svc.register_pago(pedido_id, data)
