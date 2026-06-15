from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Integer, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import utcnow


class Ingrediente(SQLModel, table=True):
    __tablename__ = "ingredientes"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(sa_column=Column(String(100), nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    es_alergeno: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, default=False),
    )
    stock_cantidad: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False, default=0),
    )
    costo_unitario: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(10, 2), nullable=False, default=0),
    )
    unidad_medida_id: int = Field(
        sa_column=Column(Integer, ForeignKey("unidades_medida.id", ondelete="RESTRICT"), nullable=False)
    )
    es_producto_terminado: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, default=False),
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

    productos_ingrediente: list["ProductoIngrediente"] = Relationship(
        back_populates="ingrediente"
    )
    unidad_medida: Optional["UnidadMedida"] = Relationship(back_populates="ingredientes")

    __table_args__ = (UniqueConstraint("nombre", name="uq_ingrediente_nombre"),)


if TYPE_CHECKING:
    from app.modules.producto_ingrediente.models import ProductoIngrediente
    from app.modules.unidad_medida.models import UnidadMedida
