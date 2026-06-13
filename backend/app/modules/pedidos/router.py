from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import DbSession
from app.modules.auth.dependencies import require_roles
from app.modules.auth.models import Usuario
from app.modules.pedidos.schemas import PedidoEstadoPatch, PedidoList
from app.modules.pedidos.service import PedidosService
from app.modules.ventas.schemas import (
    HistorialEstadoPedidoPublic,
    PagoCreate,
    PagoPublic,
    PedidoCreate,
    PedidoEstadoUpdate,
    PedidoPublic,
)

router = APIRouter()


def get_pedidos_service(session: DbSession) -> PedidosService:
    return PedidosService(session)


@router.post("/", response_model=PedidoPublic, status_code=status.HTTP_201_CREATED)
def create_pedido(
    data: PedidoCreate,
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    return svc.create_pedido(current_user.id or 0, data)


@router.get("/", response_model=PedidoList)
def list_pedidos(
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoList:
    return svc.list_pedidos_for_user(
        current_user_id=current_user.id or 0,
        page=page,
        size=size,
    )


@router.get("/{pedido_id}", response_model=PedidoPublic)
def get_pedido(
    pedido_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    usuario_id = None if svc.can_view_all(current_user.id or 0) else current_user.id
    return svc.get_pedido(pedido_id, usuario_id=usuario_id)


@router.get("/{pedido_id}/historial", response_model=list[HistorialEstadoPedidoPublic])
def get_pedido_historial(
    pedido_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "PEDIDOS", "CLIENT")),
    ],
    svc: PedidosService = Depends(get_pedidos_service),
) -> list[HistorialEstadoPedidoPublic]:
    usuario_id = None if svc.can_view_all(current_user.id or 0) else current_user.id
    return svc.get_historial(pedido_id, usuario_id=usuario_id)


@router.post("/{pedido_id}/estado", response_model=PedidoPublic)
def change_estado(
    pedido_id: Annotated[int, Path(gt=0)],
    data: PedidoEstadoUpdate,
    current_user: Annotated[Usuario, Depends(require_roles("ADMIN", "PEDIDOS"))],
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    return svc.change_estado(
        pedido_id=pedido_id,
        estado_hacia=data.estado_hacia,
        usuario_id=current_user.id,
        motivo=data.motivo,
    )


@router.patch("/{pedido_id}/estado", response_model=PedidoPublic)
def avanzar_estado(
    pedido_id: Annotated[int, Path(gt=0)],
    data: PedidoEstadoPatch,
    current_user: Annotated[Usuario, Depends(require_roles("ADMIN", "PEDIDOS"))],
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    return svc.avanzar_estado(
        pedido_id=pedido_id,
        nuevo_estado=data.nuevo_estado,
        usuario_id=current_user.id,
    )


@router.patch("/{pedido_id}/cancelar", response_model=PedidoPublic)
def cancelar_pedido(
    pedido_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    return svc.cancelar_pedido(
        pedido_id=pedido_id,
        usuario_id=current_user.id or 0,
    )


@router.delete("/{pedido_id}", response_model=PedidoPublic)
def delete_pedido(
    pedido_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "CLIENT")),
    ],
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    return svc.cancelar_pedido(
        pedido_id=pedido_id,
        usuario_id=current_user.id or 0,
    )


@router.post(
    "/{pedido_id}/pagos",
    response_model=PagoPublic,
    status_code=status.HTTP_201_CREATED,
)
def register_pago(
    pedido_id: Annotated[int, Path(gt=0)],
    data: PagoCreate,
    _current_user=Depends(require_roles("ADMIN")),
    svc: PedidosService = Depends(get_pedidos_service),
) -> PagoPublic:
    return svc.register_pago(pedido_id, data)
