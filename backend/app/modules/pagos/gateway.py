"""Wrapper aislado del SDK de MercadoPago.

Concentra todas las llamadas a la API externa de MercadoPago para que el
service no dependa directamente del SDK. No realiza acceso a la base de datos.
"""

from __future__ import annotations

import logging
from typing import Any

import mercadopago
from mercadopago.config import RequestOptions

from app.core.config import settings

logger = logging.getLogger("app.modules.pagos.gateway")


class MercadoPagoError(Exception):
    """Error al comunicarse con la API de MercadoPago."""


class MercadoPagoGateway:
    def __init__(self, access_token: str | None = None) -> None:
        token = access_token or settings.mp_access_token
        if not token:
            raise MercadoPagoError(
                "MP_ACCESS_TOKEN no configurado. Cargar la credencial en el .env"
            )
        self._sdk = mercadopago.SDK(token)

    def create_preference(
        self,
        preference_data: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Crea una preferencia de Checkout Pro y devuelve el cuerpo de la respuesta.

        Si se provee ``idempotency_key`` se envia como header ``X-Idempotency-Key``
        para evitar la creacion duplicada ante reintentos.
        """
        request_options = None
        if idempotency_key:
            request_options = RequestOptions()
            request_options.custom_headers = {"x-idempotency-key": idempotency_key}
        result = self._sdk.preference().create(preference_data, request_options)
        return self._unwrap(result, "crear la preferencia")

    def get_payment(self, payment_id: int | str) -> dict[str, Any]:
        """Consulta un pago por su id en la API de MercadoPago."""
        result = self._sdk.payment().get(payment_id)
        return self._unwrap(result, f"consultar el pago {payment_id}")

    @staticmethod
    def _unwrap(result: dict[str, Any], action: str) -> dict[str, Any]:
        status_code = result.get("status")
        response = result.get("response") or {}
        if status_code is None or status_code >= 400:
            logger.error("Error de MercadoPago al %s: %s", action, response)
            raise MercadoPagoError(f"MercadoPago fallo al {action}: {response}")
        return response
