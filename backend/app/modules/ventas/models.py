from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel

from app.core.base_model import utcnow


class FormaPago(SQLModel, table=True):
    __tablename__ = "FormaPago"

    codigo: str = Field(sa_column=Column(String(20), primary_key=True))
    descripcion: str = Field(sa_column=Column(String(80), nullable=False))
    habilitado: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, default=True),
    )


class EstadoPedido(SQLModel, table=True):
    __tablename__ = "EstadoPedido"

    codigo: str = Field(sa_column=Column(String(20), primary_key=True))
    descripcion: str = Field(sa_column=Column(String(80), nullable=False))
    orden: int = Field(sa_column=Column(Integer, nullable=False))
    es_terminal: bool = Field(sa_column=Column(Boolean, nullable=False))


class Pedido(SQLModel, table=True):
    __tablename__ = "Pedido"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    usuario_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("Usuario.id"), nullable=False),
    )
    direccion_id: int | None = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            ForeignKey("DireccionEntrega.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    estado_codigo: str = Field(
        default="PENDIENTE",
        sa_column=Column(
            String(20),
            ForeignKey("EstadoPedido.codigo"),
            nullable=False,
        ),
    )
    forma_pago_codigo: str = Field(
        sa_column=Column(
            String(20),
            ForeignKey("FormaPago.codigo"),
            nullable=False,
        ),
    )
    subtotal: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    descuento: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False, default=0),
    )
    costo_envio: Decimal = Field(
        default=Decimal("50.00"),
        sa_column=Column(Numeric(10, 2), nullable=False, default=50),
    )
    total: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    notas: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_pedido_subtotal_non_negative"),
        CheckConstraint("descuento >= 0", name="ck_pedido_descuento_non_negative"),
        CheckConstraint("costo_envio >= 0", name="ck_pedido_costo_envio_non_negative"),
        CheckConstraint("total >= 0", name="ck_pedido_total_non_negative"),
    )


class Pago(SQLModel, table=True):
    __tablename__ = "Pago"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    pedido_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("Pedido.id"), nullable=False),
    )
    mp_payment_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, unique=True, nullable=True),
    )
    mp_status: str = Field(sa_column=Column(String(30), nullable=False))
    mp_status_detail: str | None = Field(
        default=None,
        sa_column=Column(String(100), nullable=True),
    )
    external_reference: str = Field(sa_column=Column(String(100), nullable=False))
    idempotency_key: str = Field(
        sa_column=Column(String(100), nullable=False, unique=True),
    )
    transaction_amount: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False),
    )
    payment_method: str | None = Field(
        default=None,
        sa_column=Column(String(50), nullable=True),
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class HistorialEstadoPedido(SQLModel, table=True):
    __tablename__ = "HistorialEstadoPedido"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    pedido_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("Pedido.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    estado_desde: str | None = Field(
        default=None,
        sa_column=Column(
            String(20),
            ForeignKey("EstadoPedido.codigo"),
            nullable=True,
        ),
    )
    estado_hacia: str = Field(
        sa_column=Column(
            String(20),
            ForeignKey("EstadoPedido.codigo"),
            nullable=False,
        ),
    )
    usuario_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, ForeignKey("Usuario.id"), nullable=True),
    )
    motivo: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class DetallePedido(SQLModel, table=True):
    __tablename__ = "DetallePedido"

    pedido_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("Pedido.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    producto_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("productos.id", ondelete="RESTRICT"),
            primary_key=True,
        ),
    )
    cantidad: int = Field(sa_column=Column(SmallInteger, nullable=False))
    nombre_snapshot: str = Field(sa_column=Column(String(200), nullable=False))
    precio_snapshot: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    subtotal_snapshot: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    personalizacion: dict | None = Field(
        default=None,
        sa_column=Column(JSON().with_variant(JSONB, "postgresql"), nullable=True),
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    __table_args__ = (
        CheckConstraint("cantidad >= 1", name="ck_detalle_pedido_cantidad_min"),
        CheckConstraint(
            "precio_snapshot >= 0",
            name="ck_detalle_pedido_precio_snapshot_non_negative",
        ),
        CheckConstraint(
            "subtotal_snapshot >= 0",
            name="ck_detalle_pedido_subtotal_snapshot_non_negative",
        ),
    )
