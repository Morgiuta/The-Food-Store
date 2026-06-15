from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import DbSession
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import Usuario
from app.modules.auth.service import user_has_role
from app.modules.pedidos.schemas import PedidoList
from app.modules.pedidos.service import PedidosService
from app.modules.ventas.schemas import (
    EstadoPedidoPublic,
    FormaPagoPublic,
    PedidoCreate,
    PedidoEstadoUpdate,
    PedidoPublic,
    PedidoEditRequest,
)
from app.modules.ventas.service import VentasService

router = APIRouter()


def get_ventas_service(session: DbSession) -> VentasService:
    return VentasService(session)


def get_pedidos_service(session: DbSession) -> PedidosService:
    return PedidosService(session)


@router.get("/formas-pago", response_model=list[FormaPagoPublic])
def list_formas_pago(
    _current_user=Depends(require_permission("venta", "read")),
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
async def create_pedido(
    data: PedidoCreate,
    current_user: Annotated[
        Usuario,
        Depends(require_permission("pedido", "create")),
    ],
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    return await svc.create_pedido(current_user.id or 0, data)


@router.get("/pedidos", response_model=PedidoList)
def list_pedidos(
    current_user: Annotated[
        Usuario,
        Depends(require_permission("pedido", "read")),
    ],
    session: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=1000)] = 20,
    solo_hoy: Annotated[bool, Query()] = False,
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoList:
    offset = (page - 1) * size
    if current_user.id is not None and not user_has_role(
        session,
        current_user.id,
        {"ADMIN", "PEDIDOS"},
    ):
        total = svc.pedidos.count_by_usuario(current_user.id, solo_hoy=solo_hoy)
        return PedidoList(
            items=[
                svc.get_pedido(pedido.id or 0)
                for pedido in svc.pedidos.get_by_usuario(
                    current_user.id,
                    offset=offset,
                    limit=size,
                    solo_hoy=solo_hoy,
                )
            ],
            total=total,
            page=page,
            size=size,
            pages=max(1, (total + size - 1) // size),
        )
    total = svc.pedidos.count_all(solo_hoy=solo_hoy)
    return PedidoList(
        items=[
            svc.get_pedido(pedido.id or 0)
            for pedido in svc.pedidos.get_all(offset=offset, limit=size, solo_hoy=solo_hoy)
        ],
        total=total,
        page=page,
        size=size,
        pages=max(1, (total + size - 1) // size),
    )


@router.get("/pedidos/{pedido_id}", response_model=PedidoPublic)
def get_pedido(
    pedido_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[
        Usuario,
        Depends(require_permission("pedido", "read")),
    ],
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
async def change_estado(
    pedido_id: Annotated[int, Path(gt=0)],
    data: PedidoEstadoUpdate,
    current_user: Annotated[Usuario, Depends(require_permission("pedido", "update"))],
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    return await svc.change_estado(
        pedido_id=pedido_id,
        estado_hacia=data.estado_hacia,
        usuario_id=current_user.id,
        motivo=data.motivo,
    )


@router.patch("/pedidos/{pedido_id}/editar", response_model=PedidoPublic)
async def editar_pedido(
    pedido_id: Annotated[int, Path(gt=0)],
    data: PedidoEditRequest,
    current_user: Annotated[Usuario, Depends(require_permission("pedido", "create"))],
    session: DbSession,
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    is_staff = False
    if current_user.id is not None and user_has_role(session, current_user.id, {"ADMIN", "PEDIDOS"}):
        is_staff = True
    return await svc.editar_pedido(
        pedido_id=pedido_id,
        usuario_id=current_user.id or 0,
        data=data,
        is_staff=is_staff,
    )
