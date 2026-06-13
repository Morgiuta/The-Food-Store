from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.types import JSON
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import utcnow


class Producto(SQLModel, table=True):
    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(sa_column=Column(String(150), nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    precio_base: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False)
    )
    imagen_url: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    imagenes_url: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    stock_cantidad: int = Field(default=0, sa_column=Column(Integer, nullable=False, default=0))
    unidad_venta_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("unidades_medida.id"),
            nullable=True,
        ),
    )
    tiempo_prep_min: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    disponible: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, default=True),
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    productos_categoria: list["ProductoCategoria"] = Relationship(back_populates="producto")
    productos_ingrediente: list["ProductoIngrediente"] = Relationship(back_populates="producto")
    detalles_pedido: list["DetallePedido"] = Relationship(back_populates="producto")
    unidad_venta: Optional["UnidadMedida"] = Relationship(back_populates="productos")

    __table_args__ = (
        CheckConstraint("precio_base >= 0", name="ck_producto_precio_base_non_negative"),
        CheckConstraint("stock_cantidad >= 0", name="ck_producto_stock_non_negative"),
        CheckConstraint(
            "tiempo_prep_min IS NULL OR tiempo_prep_min >= 0",
            name="ck_producto_tiempo_prep_min_non_negative",
        ),
    )


if TYPE_CHECKING:
    from app.modules.producto_categoria.models import ProductoCategoria
    from app.modules.producto_ingrediente.models import ProductoIngrediente
    from app.modules.unidad_medida.models import UnidadMedida
    from app.modules.ventas.models import DetallePedido
