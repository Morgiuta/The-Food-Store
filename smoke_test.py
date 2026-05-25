from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from typing import Any

try:
    import httpx
except ImportError:  # pragma: no cover - fallback for minimal environments
    httpx = None

try:
    import requests
except ImportError:  # pragma: no cover - fallback for minimal environments
    requests = None


BASE_URL = os.getenv("SMOKE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
ADMIN_EMAIL = os.getenv("SMOKE_ADMIN_EMAIL", "admin@admin.com")
ADMIN_PASSWORD = os.getenv("SMOKE_ADMIN_PASSWORD", "admin123")


@dataclass
class StepResult:
    name: str
    passed: bool
    detail: str = ""


class SmokeClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.uses_httpx = httpx is not None
        if self.uses_httpx:
            self.client = httpx.Client(base_url=base_url, timeout=10.0, follow_redirects=True)
            return
        if requests is not None:
            self.client = requests.Session()
            return
        raise RuntimeError("Instalar httpx o requests para ejecutar este smoke test.")

    def close(self) -> None:
        close = getattr(self.client, "close", None)
        if close is not None:
            close()

    def _url(self, path: str) -> str:
        return path if self.uses_httpx else f"{self.base_url}{path}"

    def get(self, path: str, **kwargs: Any) -> Any:
        if self.uses_httpx:
            return self.client.get(path, **kwargs)
        return self.client.get(self._url(path), timeout=10.0, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Any:
        if self.uses_httpx:
            return self.client.post(path, **kwargs)
        return self.client.post(self._url(path), timeout=10.0, allow_redirects=True, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Any:
        if self.uses_httpx:
            return self.client.patch(path, **kwargs)
        return self.client.patch(self._url(path), timeout=10.0, allow_redirects=True, **kwargs)


def print_result(result: StepResult) -> None:
    status = "PASS" if result.passed else "FAIL"
    suffix = f" - {result.detail}" if result.detail else ""
    print(f"{status} {result.name}{suffix}")


def json_or_none(response: Any) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


def login(client: SmokeClient, email: str, password: str) -> tuple[bool, str]:
    attempts = [
        (
            "/auth/login",
            {"json": {"email": email, "password": password}},
            "POST /auth/login JSON",
        ),
        (
            "/auth/login",
            {"data": {"username": email, "password": password}},
            "POST /auth/login form",
        ),
        (
            "/auth/token",
            {"data": {"username": email, "password": password}},
            "POST /auth/token form",
        ),
    ]

    for path, kwargs, label in attempts:
        response = client.post(path, **kwargs)
        if response.status_code != 200:
            continue

        body = json_or_none(response)
        token = body.get("access_token") if isinstance(body, dict) else None
        if token:
            client.client.headers["Authorization"] = f"Bearer {token}"
            return True, f"{label}; token bearer recibido"

        cookie_token = client.client.cookies.get("access_token")
        if cookie_token:
            return True, f"{label}; cookie access_token recibida"

        return False, f"{label}; login 200 sin access_token ni cookie access_token"

    return False, "login no devolvio 200 en /auth/login ni /auth/token"


def extract_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return [item for item in payload["items"] if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def find_valid_product(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in items:
        if item.get("id") and item.get("disponible") is True and item.get("stock_cantidad", 0) >= 1:
            return item
    return None


def run() -> int:
    results: list[StepResult] = []
    unique = int(time.time())
    user_email = f"smoke_{unique}@example.com"
    user_password = "Smoke123!"
    client = SmokeClient(BASE_URL)

    try:
        response = client.post(
            "/auth/register",
            json={
                "nombre": f"Smoke {unique}",
                "email": user_email,
                "password": user_password,
            },
        )
        data = json_or_none(response)
        user_id = data.get("id") if isinstance(data, dict) else None
        results.append(
            StepResult(
                "1. POST /auth/register crea usuario CLIENT",
                response.status_code == 201 and bool(user_id),
                f"HTTP {response.status_code}, user_id={user_id}",
            )
        )

        ok, detail = login(client, user_email, user_password)
        results.append(StepResult("2. POST /auth/login obtiene token", ok, detail))

        response = client.get(
            "/productos/",
            params={"q": "", "disponible": "true", "page": 1},
        )
        product_payload = json_or_none(response)
        products = extract_items(product_payload)
        product = find_valid_product(products)
        results.append(
            StepResult(
                "3. GET /productos/ q= disponible=true page=1 responde 200",
                response.status_code == 200,
                f"HTTP {response.status_code}, productos={len(products)}",
            )
        )

        response = client.post(
            "/direcciones/",
            json={
                "calle": "Calle Smoke",
                "numero": str(unique % 10000),
                "ciudad": "Buenos Aires",
                "provincia": "Buenos Aires",
                "codigo_postal": "1000",
                "es_principal": False,
            },
        )
        address_payload = json_or_none(response)
        address_id = address_payload.get("id") if isinstance(address_payload, dict) else None
        results.append(
            StepResult(
                "4. POST /direcciones/ autenticado como CLIENT crea direccion",
                response.status_code == 201 and bool(address_id),
                f"HTTP {response.status_code}, direccion_id={address_id}",
            )
        )

        response = client.patch(f"/direcciones/{address_id}/principal") if address_id else None
        results.append(
            StepResult(
                "5. PATCH /direcciones/{id}/principal responde 200",
                response is not None and response.status_code == 200,
                f"HTTP {response.status_code}" if response is not None else "sin direccion_id",
            )
        )

        order_id = None
        if product is None:
            results.append(
                StepResult(
                    "6. POST /pedidos/ con producto valido crea pedido PENDIENTE",
                    False,
                    "no hay producto disponible con stock en la respuesta de /productos/",
                )
            )
        else:
            response = client.post(
                "/pedidos/",
                json={
                    "direccion_id": address_id,
                    "forma_pago_codigo": "EFECTIVO",
                    "descuento": "0.00",
                    "costo_envio": "50.00",
                    "notas": "Smoke test",
                    "detalles": [{"producto_id": product["id"], "cantidad": 1}],
                },
            )
            order_payload = json_or_none(response)
            order_id = order_payload.get("id") if isinstance(order_payload, dict) else None
            order_state = order_payload.get("estado_codigo") if isinstance(order_payload, dict) else None
            results.append(
                StepResult(
                    "6. POST /pedidos/ con producto valido crea pedido PENDIENTE",
                    response.status_code == 201 and bool(order_id) and order_state == "PENDIENTE",
                    f"HTTP {response.status_code}, pedido_id={order_id}, estado={order_state}",
                )
            )

        admin_client = SmokeClient(BASE_URL)
        ok, detail = login(admin_client, ADMIN_EMAIL, ADMIN_PASSWORD)
        results.append(StepResult("7. Login como admin obtiene token admin", ok, detail))

        response = admin_client.get("/admin/usuarios/", params={"rol": "CLIENT"})
        admin_users_payload = json_or_none(response)
        admin_users = extract_items(admin_users_payload)
        results.append(
            StepResult(
                "8. GET /admin/usuarios/?rol=CLIENT lista usuarios",
                response.status_code == 200,
                f"HTTP {response.status_code}, usuarios={len(admin_users)}",
            )
        )

        if order_id is None:
            results.append(
                StepResult(
                    "9. PATCH /pedidos/{id}/estado con admin avanza a CONFIRMADO",
                    False,
                    "sin pedido_id",
                )
            )
        else:
            response = admin_client.patch(
                f"/pedidos/{order_id}/estado",
                json={"nuevo_estado": "CONFIRMADO"},
            )
            order_payload = json_or_none(response)
            order_state = order_payload.get("estado_codigo") if isinstance(order_payload, dict) else None
            results.append(
                StepResult(
                    "9. PATCH /pedidos/{id}/estado con admin avanza a CONFIRMADO",
                    response.status_code == 200 and order_state == "CONFIRMADO",
                    f"HTTP {response.status_code}, estado={order_state}",
                )
            )

        if order_id is None:
            results.append(
                StepResult(
                    "10. PATCH /pedidos/{id}/cancelar como CLIENT responde 422 o 200",
                    False,
                    "sin pedido_id",
                )
            )
        else:
            response = client.patch(f"/pedidos/{order_id}/cancelar")
            results.append(
                StepResult(
                    "10. PATCH /pedidos/{id}/cancelar como CLIENT responde 422 o 200",
                    response.status_code in {200, 422},
                    f"HTTP {response.status_code}",
                )
            )

        admin_client.close()
    except Exception as exc:
        request_errors = []
        if httpx is not None:
            request_errors.append(httpx.RequestError)
        if requests is not None:
            request_errors.append(requests.RequestException)
        if request_errors and not isinstance(exc, tuple(request_errors)):
            raise
        results.append(
            StepResult(
                "conexion con API",
                False,
                f"{exc.__class__.__name__}: {exc}",
            )
        )
    finally:
        client.close()

    for result in results:
        print_result(result)

    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    sys.exit(run())
