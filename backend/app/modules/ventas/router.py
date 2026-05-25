from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import DbSession
from app.modules.auth.dependencies import require_roles
from app.modules.auth.models import Usuario
from app.modules.auth.service import user_has_role
from app.modules.pedidos.schemas import PedidoList
from app.modules.pedidos.service import PedidosService
from app.modules.ventas.schemas import (
    EstadoPedidoPublic,
    FormaPagoPublic,
    PagoCreate,
    PagoPublic,
    PedidoCreate,
    PedidoEstadoUpdate,
    PedidoPublic,
)
from app.modules.ventas.service import VentasService

router = APIRouter()


def get_ventas_service(session: DbSession) -> VentasService:
    return VentasService(session)


def get_pedidos_service(session: DbSession) -> PedidosService:
    return PedidosService(session)


@router.get("/formas-pago", response_model=list[FormaPagoPublic])
def list_formas_pago(
    _current_user=Depends(require_roles("ADMIN", "CLIENT")),
    svc: VentasService = Depends(get_ventas_service),
) -> list[FormaPagoPublic]:
    return svc.list_formas_pago()


@router.get("/estados", response_model=list[EstadoPedidoPublic])
def list_estados(
    _current_user=Depends(require_roles("ADMIN", "PEDIDOS")),
    svc: VentasService = Depends(get_ventas_service),
) -> list[EstadoPedidoPublic]:
    return svc.list_estados()


@router.post("/pedidos", response_model=PedidoPublic, status_code=status.HTTP_201_CREATED)
def create_pedido(
    data: PedidoCreate,
    current_user: Annotated[Usuario, Depends(require_roles("ADMIN", "CLIENT"))],
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    return svc.create_pedido(current_user.id or 0, data)


@router.get("/pedidos", response_model=PedidoList)
def list_pedidos(
    current_user: Annotated[Usuario, Depends(require_roles("ADMIN", "PEDIDOS", "CLIENT"))],
    session: DbSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 20,
    solo_hoy: Annotated[bool, Query()] = False,
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoList:
    if current_user.id is not None and not user_has_role(
        session,
        current_user.id,
        {"ADMIN", "PEDIDOS"},
    ):
        return PedidoList(
            items=[
                svc.get_pedido(pedido.id or 0)
                for pedido in svc.pedidos.get_by_usuario(
                    current_user.id,
                    offset=offset,
                    limit=limit,
                    solo_hoy=solo_hoy,
                )
            ],
            total=svc.pedidos.count_by_usuario(current_user.id, solo_hoy=solo_hoy),
            page=(offset // limit) + 1,
            limit=limit,
        )
    return PedidoList(
        items=[
            svc.get_pedido(pedido.id or 0)
            for pedido in svc.pedidos.get_all(offset=offset, limit=limit, solo_hoy=solo_hoy)
        ],
        total=svc.pedidos.count_all(solo_hoy=solo_hoy),
        page=(offset // limit) + 1,
        limit=limit,
    )


@router.get("/pedidos/{pedido_id}", response_model=PedidoPublic)
def get_pedido(
    pedido_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[Usuario, Depends(require_roles("ADMIN", "PEDIDOS", "CLIENT"))],
    session: DbSession,
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    usuario_id = None
    if current_user.id is not None and not user_has_role(
        session,
        current_user.id,
        {"ADMIN", "PEDIDOS"},
    ):
        usuario_id = current_user.id
    return svc.get_pedido(pedido_id, usuario_id=usuario_id)


@router.post("/pedidos/{pedido_id}/estado", response_model=PedidoPublic)
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


@router.post(
    "/pedidos/{pedido_id}/pagos",
    response_model=PagoPublic,
    status_code=status.HTTP_201_CREATED,
)
def register_pago(
    pedido_id: Annotated[int, Path(gt=0)],
    data: PagoCreate,
    _current_user=Depends(require_roles("ADMIN")),
    svc: VentasService = Depends(get_ventas_service),
) -> PagoPublic:
    return svc.register_pago(pedido_id, data)
