from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlmodel import Field, SQLModel

from app.shared.schemas.pagination import PaginatedResponse


class DetallePedidoCreate(SQLModel):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(ge=1)
    personalizacion: dict[str, Any] | None = None


class PedidoCreate(SQLModel):
    direccion_id: int | None = Field(default=None, gt=0)
    forma_pago_codigo: str = Field(min_length=1, max_length=20)
    descuento: Decimal = Field(default=Decimal("0.00"), ge=0)
    costo_envio: Decimal = Field(default=Decimal("50.00"), ge=0)
    notas: str | None = None
    detalles: list[DetallePedidoCreate] = Field(min_length=1)


class PedidoEstadoUpdate(SQLModel):
    estado_hacia: str = Field(min_length=1, max_length=20)
    motivo: str | None = None


class PagoCreate(SQLModel):
    mp_payment_id: int | None = None
    mp_status: str = Field(min_length=1, max_length=30)
    mp_status_detail: str | None = Field(default=None, max_length=100)
    external_reference: str = Field(min_length=1, max_length=100)
    idempotency_key: str = Field(min_length=1, max_length=100)
    transaction_amount: Decimal = Field(ge=0)
    payment_method: str | None = Field(default=None, max_length=50)


class FormaPagoPublic(SQLModel):
    codigo: str
    descripcion: str
    habilitado: bool


class EstadoPedidoPublic(SQLModel):
    codigo: str
    descripcion: str
    orden: int
    es_terminal: bool


class DetallePedidoPublic(SQLModel):
    pedido_id: int
    producto_id: int
    cantidad: int
    nombre_snapshot: str
    precio_snapshot: Decimal
    subtotal_snapshot: Decimal
    personalizacion: dict[str, Any] | None
    created_at: datetime


class PagoPublic(SQLModel):
    id: int
    pedido_id: int
    mp_payment_id: int | None
    mp_status: str
    mp_status_detail: str | None
    external_reference: str
    idempotency_key: str
    transaction_amount: Decimal
    payment_method: str | None
    created_at: datetime
    updated_at: datetime


class HistorialEstadoPedidoPublic(SQLModel):
    id: int
    pedido_id: int
    estado_desde: str | None
    estado_hacia: str
    usuario_id: int | None
    motivo: str | None
    created_at: datetime


class PedidoPublic(SQLModel):
    id: int
    usuario_id: int
    direccion_id: int | None
    estado_codigo: str
    forma_pago_codigo: str
    subtotal: Decimal
    descuento: Decimal
    costo_envio: Decimal
    total: Decimal
    notas: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    detalles: list[DetallePedidoPublic]
    pagos: list[PagoPublic]
    historial: list[HistorialEstadoPedidoPublic]


class PedidoList(PaginatedResponse[PedidoPublic]):
    pass
