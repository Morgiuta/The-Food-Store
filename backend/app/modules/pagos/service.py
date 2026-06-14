from __future__ import annotations

import hashlib
import hmac
import logging
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlmodel import Session

from app.core.base_model import utcnow
from app.core.config import settings
from app.modules.pagos.gateway import MercadoPagoError, MercadoPagoGateway
from app.modules.pagos.schemas import CrearPagoResponse, PagoPublic
from app.modules.pagos.unit_of_work import PagosUnitOfWork
from app.modules.pedidos.service import PedidosService
from app.modules.ventas.models import Pago

logger = logging.getLogger("app.modules.pagos.service")

FORMA_PAGO_MP = "MERCADOPAGO"

MP_STATUS_APROBADO = "approved"
MP_STATUS_RECHAZADO = {"rejected", "cancelled", "refunded", "charged_back"}


class PagosService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear_preferencia(
        self,
        pedido_id: int,
        usuario_id: int,
        is_staff: bool,
    ) -> CrearPagoResponse:
        if not settings.mp_access_token:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MercadoPago no esta configurado en el servidor",
            )

        items_preferencia: list[dict] = []
        external_reference: str
        idempotency_key: str

        with PagosUnitOfWork(self.session) as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if pedido is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pedido con id={pedido_id} no encontrado",
                )
            if not is_staff and pedido.usuario_id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pedido con id={pedido_id} no encontrado",
                )
            if pedido.estado_codigo != "PENDIENTE":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Solo se puede pagar un pedido en estado PENDIENTE",
                )
            if pedido.forma_pago_codigo != FORMA_PAGO_MP:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El pedido no usa MercadoPago como forma de pago",
                )

            external_reference = str(pedido.id)

            pago = uow.pagos.get_by_pedido_id(pedido.id or 0)
            if pago is None:
                pago = uow.pagos.create(
                    Pago(
                        pedido_id=pedido.id or 0,
                        mp_status="pending",
                        external_reference=external_reference,
                        idempotency_key=str(uuid4()),
                        transaction_amount=pedido.total,
                    )
                )
            idempotency_key = pago.idempotency_key

            for detalle in uow.pedidos.list_detalles(pedido.id or 0):
                items_preferencia.append(
                    {
                        "title": detalle.nombre_snapshot,
                        "quantity": detalle.cantidad,
                        "unit_price": float(detalle.precio_snapshot),
                        "currency_id": "ARS",
                    }
                )
            if pedido.costo_envio and pedido.costo_envio > 0:
                items_preferencia.append(
                    {
                        "title": "Costo de envio",
                        "quantity": 1,
                        "unit_price": float(pedido.costo_envio),
                        "currency_id": "ARS",
                    }
                )
            if pedido.descuento and pedido.descuento > 0:
                items_preferencia.append(
                    {
                        "title": "Descuento",
                        "quantity": 1,
                        "unit_price": -float(pedido.descuento),
                        "currency_id": "ARS",
                    }
                )

        preference_data = {
            "items": items_preferencia,
            "external_reference": external_reference,
            "back_urls": {
                "success": f"{settings.frontend_url}/checkout/pago/exito",
                "failure": f"{settings.frontend_url}/checkout/pago/fallo",
                "pending": f"{settings.frontend_url}/checkout/pago/pendiente",
            },
            "metadata": {"pedido_id": pedido_id},
        }
        if settings.mp_notification_url:
            preference_data["notification_url"] = settings.mp_notification_url

        try:
            gateway = MercadoPagoGateway()
            response = gateway.create_preference(preference_data, idempotency_key=idempotency_key)
        except MercadoPagoError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="No se pudo crear la preferencia de pago en MercadoPago",
            ) from exc

        return CrearPagoResponse(
            pedido_id=pedido_id,
            preference_id=str(response.get("id", "")),
            init_point=response.get("init_point", ""),
            sandbox_init_point=response.get("sandbox_init_point"),
            public_key=settings.mp_public_key,
        )

    async def procesar_webhook(
        self,
        topic: str | None,
        data_id: str | None,
        x_signature: str | None,
        x_request_id: str | None,
    ) -> None:
        if topic not in {"payment", "payments"}:
            return

        if not data_id:
            return

        self._validar_firma(data_id, x_signature, x_request_id)

        try:
            gateway = MercadoPagoGateway()
            payment = gateway.get_payment(data_id)
        except MercadoPagoError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="No se pudo consultar el pago en MercadoPago",
            ) from exc

        external_reference = payment.get("external_reference")
        mp_status = payment.get("status")
        if not external_reference or not mp_status:
            return

        try:
            pedido_id = int(external_reference)
        except (TypeError, ValueError):
            return

        confirmar = False
        cancelar = False
        motivo: str | None = None

        with PagosUnitOfWork(self.session) as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if pedido is None:
                return

            pago = uow.pagos.get_by_pedido_id(pedido_id)
            if pago is None:
                pago = Pago(
                    pedido_id=pedido_id,
                    external_reference=external_reference,
                    idempotency_key=str(uuid4()),
                    transaction_amount=Decimal(str(payment.get("transaction_amount", 0))),
                    mp_status=mp_status,
                )

            pago.mp_payment_id = int(payment["id"]) if payment.get("id") else pago.mp_payment_id
            pago.mp_status = mp_status
            pago.mp_status_detail = payment.get("status_detail")
            pago.payment_method = payment.get("payment_method_id")
            if payment.get("transaction_amount") is not None:
                pago.transaction_amount = Decimal(str(payment["transaction_amount"]))
            pago.updated_at = utcnow()
            uow.pagos.update(pago)

            if mp_status == MP_STATUS_APROBADO and pedido.estado_codigo == "PENDIENTE":
                confirmar = True
            elif mp_status in MP_STATUS_RECHAZADO and pedido.estado_codigo in {
                "PENDIENTE",
                "CONFIRMADO",
            }:
                cancelar = True
                motivo = f"Pago {mp_status}: {payment.get('status_detail') or ''}".strip()

        if confirmar or cancelar:
            pedidos_service = PedidosService(self.session)
            await pedidos_service.change_estado(
                pedido_id=pedido_id,
                estado_hacia="CONFIRMADO" if confirmar else "CANCELADO",
                usuario_id=None,
                motivo=motivo,
            )

    def obtener_pago(
        self,
        pedido_id: int,
        usuario_id: int,
        is_staff: bool,
    ) -> PagoPublic:
        with PagosUnitOfWork(self.session) as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if pedido is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pedido con id={pedido_id} no encontrado",
                )
            if not is_staff and pedido.usuario_id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pedido con id={pedido_id} no encontrado",
                )

            pago = uow.pagos.get_by_pedido_id(pedido_id)
            if pago is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No hay pago registrado para el pedido id={pedido_id}",
                )
            return PagoPublic.model_validate(pago)

    def _validar_firma(
        self,
        data_id: str,
        x_signature: str | None,
        x_request_id: str | None,
    ) -> None:
        """Valida la firma del webhook (header x-signature) de MercadoPago.

        Formato del header: ``ts=<timestamp>,v1=<hmac_sha256>``.
        El manifiesto firmado es ``id:<data_id>;request-id:<x_request_id>;ts:<ts>;``.
        """
        if not settings.mp_webhook_secret:
            logger.warning(
                "MP_WEBHOOK_SECRET no configurado: se omite la validacion de firma"
            )
            return

        if not x_signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firma de webhook ausente",
            )

        ts: str | None = None
        v1: str | None = None
        for part in x_signature.split(","):
            key, _, value = part.partition("=")
            key = key.strip()
            value = value.strip()
            if key == "ts":
                ts = value
            elif key == "v1":
                v1 = value

        if not ts or not v1:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firma de webhook invalida",
            )

        manifest = f"id:{data_id.lower()};request-id:{x_request_id or ''};ts:{ts};"
        expected = hmac.new(
            settings.mp_webhook_secret.encode("utf-8"),
            manifest.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected, v1):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firma de webhook no valida",
            )
