from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

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
from sqlmodel import Field, Relationship, SQLModel

from app.core.base_model import utcnow


class FormaPago(SQLModel, table=True):
    __tablename__ = "formas_pago"

    codigo: str = Field(sa_column=Column(String(20), primary_key=True))
    descripcion: str = Field(sa_column=Column(String(80), nullable=False))
    habilitado: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, default=True),
    )
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    pedidos: list["Pedido"] = Relationship(back_populates="forma_pago")


class EstadoPedido(SQLModel, table=True):
    __tablename__ = "estados_pedido"

    codigo: str = Field(sa_column=Column(String(20), primary_key=True))
    descripcion: str = Field(sa_column=Column(String(80), nullable=False))
    orden: int = Field(sa_column=Column(Integer, nullable=False))
    es_terminal: bool = Field(sa_column=Column(Boolean, nullable=False))
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    pedidos: list["Pedido"] = Relationship(back_populates="estado")
    historial_desde: list["HistorialEstadoPedido"] = Relationship(
        back_populates="estado_desde_rel",
        sa_relationship_kwargs={
            "foreign_keys": "[HistorialEstadoPedido.estado_desde]",
        },
    )
    historial_hacia: list["HistorialEstadoPedido"] = Relationship(
        back_populates="estado_hacia_rel",
        sa_relationship_kwargs={
            "foreign_keys": "[HistorialEstadoPedido.estado_hacia]",
        },
    )


class Pedido(SQLModel, table=True):
    __tablename__ = "pedidos"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    usuario_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("usuarios.id"), nullable=False),
    )
    direccion_id: int | None = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            ForeignKey("direcciones_entrega.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    estado_codigo: str = Field(
        default="PENDIENTE",
        sa_column=Column(
            String(20),
            ForeignKey("estados_pedido.codigo"),
            nullable=False,
        ),
    )
    forma_pago_codigo: str = Field(
        sa_column=Column(
            String(20),
            ForeignKey("formas_pago.codigo"),
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

    detalles: list["DetallePedido"] = Relationship(back_populates="pedido")
    historial: list["HistorialEstadoPedido"] = Relationship(back_populates="pedido")
    pagos: list["Pago"] = Relationship(back_populates="pedido")
    usuario: "Usuario" = Relationship(back_populates="pedidos")
    estado: EstadoPedido = Relationship(back_populates="pedidos")
    forma_pago: FormaPago = Relationship(back_populates="pedidos")

    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_pedido_subtotal_non_negative"),
        CheckConstraint("descuento >= 0", name="ck_pedido_descuento_non_negative"),
        CheckConstraint("costo_envio >= 0", name="ck_pedido_costo_envio_non_negative"),
        CheckConstraint("total >= 0", name="ck_pedido_total_non_negative"),
    )


class Pago(SQLModel, table=True):
    __tablename__ = "pagos"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    pedido_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("pedidos.id"), nullable=False),
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
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    pedido: Pedido = Relationship(back_populates="pagos")


class HistorialEstadoPedido(SQLModel, table=True):
    __tablename__ = "historial_estados_pedido"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    pedido_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("pedidos.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    estado_desde: str | None = Field(
        default=None,
        sa_column=Column(
            String(20),
            ForeignKey("estados_pedido.codigo"),
            nullable=True,
        ),
    )
    estado_hacia: str = Field(
        sa_column=Column(
            String(20),
            ForeignKey("estados_pedido.codigo"),
            nullable=False,
        ),
    )
    usuario_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, ForeignKey("usuarios.id"), nullable=True),
    )
    motivo: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    pedido: Pedido = Relationship(back_populates="historial")
    usuario: Optional["Usuario"] = Relationship(back_populates="historial_pedidos")
    estado_desde_rel: Optional[EstadoPedido] = Relationship(
        back_populates="historial_desde",
        sa_relationship_kwargs={
            "foreign_keys": "[HistorialEstadoPedido.estado_desde]",
        },
    )
    estado_hacia_rel: EstadoPedido = Relationship(
        back_populates="historial_hacia",
        sa_relationship_kwargs={
            "foreign_keys": "[HistorialEstadoPedido.estado_hacia]",
        },
    )


class DetallePedido(SQLModel, table=True):
    __tablename__ = "detalle_pedidos"

    pedido_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("pedidos.id", ondelete="CASCADE"),
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
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    pedido: Pedido = Relationship(back_populates="detalles")
    producto: "Producto" = Relationship(back_populates="detalles_pedido")

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


if TYPE_CHECKING:
    from app.modules.auth.models import Usuario
    from app.modules.producto.models import Producto
