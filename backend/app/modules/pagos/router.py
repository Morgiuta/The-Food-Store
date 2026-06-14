from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request, status

from app.api.deps import DbSession
from app.modules.auth.dependencies import require_roles
from app.modules.auth.models import Usuario
from app.modules.auth.service import user_has_role
from app.modules.pagos.schemas import (
    CrearPagoRequest,
    CrearPagoResponse,
    PagoPublic,
    WebhookResponse,
)
from app.modules.pagos.service import PagosService

router = APIRouter()

STAFF_ROLES = {"ADMIN", "PEDIDOS"}


def get_pagos_service(session: DbSession) -> PagosService:
    return PagosService(session)


def _is_staff(session: DbSession, usuario_id: int | None) -> bool:
    return usuario_id is not None and user_has_role(session, usuario_id, STAFF_ROLES)


@router.post(
    "/crear",
    response_model=CrearPagoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_pago(
    data: CrearPagoRequest,
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    session: DbSession,
    svc: PagosService = Depends(get_pagos_service),
) -> CrearPagoResponse:
    return svc.crear_preferencia(
        pedido_id=data.pedido_id,
        usuario_id=current_user.id or 0,
        is_staff=_is_staff(session, current_user.id),
    )


@router.post("/webhook", response_model=WebhookResponse)
async def webhook(
    request: Request,
    svc: PagosService = Depends(get_pagos_service),
) -> WebhookResponse:
    topic = request.query_params.get("type") or request.query_params.get("topic")
    data_id = request.query_params.get("data.id") or request.query_params.get("id")

    if topic is None or data_id is None:
        try:
            body = await request.json()
        except Exception:
            body = {}
        if isinstance(body, dict):
            topic = topic or body.get("type") or body.get("topic")
            data = body.get("data")
            if data_id is None and isinstance(data, dict):
                data_id = data.get("id")
            data_id = data_id or body.get("id")

    await svc.procesar_webhook(
        topic=topic,
        data_id=str(data_id) if data_id is not None else None,
        x_signature=request.headers.get("x-signature"),
        x_request_id=request.headers.get("x-request-id"),
    )
    return WebhookResponse()


@router.get("/{pedido_id}", response_model=PagoPublic)
def get_pago(
    pedido_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    session: DbSession,
    svc: PagosService = Depends(get_pagos_service),
) -> PagoPublic:
    return svc.obtener_pago(
        pedido_id=pedido_id,
        usuario_id=current_user.id or 0,
        is_staff=_is_staff(session, current_user.id),
    )
