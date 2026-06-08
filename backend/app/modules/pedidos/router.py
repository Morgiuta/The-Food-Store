from typing import Annotated
import json

from fastapi import APIRouter, Depends, Path, Query, WebSocket, WebSocketDisconnect, status
from sqlmodel import Session

from app.api.deps import DbSession
from app.core.database import engine
from app.core.security import decode_access_token
from app.modules.auth.dependencies import require_roles
from app.modules.auth.models import Usuario
from app.modules.auth.service import get_user_by_username, get_user_role_codes
from app.modules.pedidos.repository import PedidoRepository
from app.modules.pedidos.schemas import PedidoEstadoPatch, PedidoList
from app.modules.pedidos.service import PedidosService
from app.modules.ventas.schemas import (
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
async def create_pedido(
    data: PedidoCreate,
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    return await svc.create_pedido(current_user.id or 0, data)


@router.get("/", response_model=PedidoList)
def list_pedidos(
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoList:
    return svc.list_pedidos_for_user(
        current_user_id=current_user.id or 0,
        page=page,
        limit=limit,
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


@router.post("/{pedido_id}/estado", response_model=PedidoPublic)
async def change_estado(
    pedido_id: Annotated[int, Path(gt=0)],
    data: PedidoEstadoUpdate,
    current_user: Annotated[Usuario, Depends(require_roles("ADMIN", "PEDIDOS"))],
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    return await svc.change_estado(
        pedido_id=pedido_id,
        estado_hacia=data.estado_hacia,
        usuario_id=current_user.id,
        motivo=data.motivo,
    )


@router.patch("/{pedido_id}/estado", response_model=PedidoPublic)
async def avanzar_estado(
    pedido_id: Annotated[int, Path(gt=0)],
    data: PedidoEstadoPatch,
    current_user: Annotated[Usuario, Depends(require_roles("ADMIN", "PEDIDOS"))],
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    return await svc.avanzar_estado(
        pedido_id=pedido_id,
        nuevo_estado=data.nuevo_estado,
        usuario_id=current_user.id,
    )


@router.patch("/{pedido_id}/cancelar", response_model=PedidoPublic)
async def cancelar_pedido(
    pedido_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    svc: PedidosService = Depends(get_pedidos_service),
) -> PedidoPublic:
    return await svc.cancelar_pedido(
        pedido_id=pedido_id,
        usuario_id=current_user.id or 0,
    )


@router.post(
    "/{pedido_id}/pagos",
    response_model=PagoPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register_pago(
    pedido_id: Annotated[int, Path(gt=0)],
    data: PagoCreate,
    _current_user=Depends(require_roles("ADMIN")),
    svc: PedidosService = Depends(get_pedidos_service),
) -> PagoPublic:
    return await svc.register_pago(pedido_id, data)


def _get_ws_token(websocket: WebSocket) -> str | None:
    token = websocket.cookies.get("access_token")
    if token:
        return token

    authorization = websocket.headers.get("authorization")
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:]

    return None


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    token = _get_ws_token(websocket)
    if not token:
        await websocket.accept()
        await websocket.close(code=1008, reason="Token de autenticacion requerido")
        return

    payload = decode_access_token(token)
    username = payload.get("sub") if payload else None
    if not username:
        await websocket.accept()
        await websocket.close(code=1008, reason="Token invalido o expirado")
        return

    with Session(engine) as session:
        user = get_user_by_username(session, username)
        if user is None or not user.is_active or user.id is None:
            await websocket.accept()
            await websocket.close(code=1008, reason="Usuario invalido o inactivo")
            return

        user_id = user.id
        user_roles = get_user_role_codes(session, user_id)

    from app.core.websocket import manager

    await manager.connect(websocket, roles=user_roles, user_id=user_id)
    is_staff = bool({"ADMIN", "STOCK", "PEDIDOS"}.intersection(set(user_roles)))

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                continue

            action = message.get("action")
            order_id = message.get("order_id")
            if not isinstance(order_id, int) or order_id <= 0:
                continue

            if action == "subscribe-order":
                if not is_staff:
                    with Session(engine) as session:
                        pedido = PedidoRepository(session).get_by_id(order_id)
                        if pedido is None or pedido.usuario_id != user_id:
                            await websocket.send_json(
                                {
                                    "event": "ERROR",
                                    "data": {
                                        "detail": "No autorizado para este pedido",
                                    },
                                }
                            )
                            continue

                manager.join_order_room(websocket, order_id)
                await websocket.send_json(
                    {"event": "SUBSCRIBED", "data": {"order_id": order_id}}
                )

            elif action == "unsubscribe-order":
                manager.leave_order_room(websocket, order_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
