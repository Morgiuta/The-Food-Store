from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Numeric
from sqlmodel import Field, Relationship, SQLModel


class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingrediente"

    producto_id: int = Field(
        sa_column=Column(ForeignKey("productos.id", ondelete="CASCADE"), primary_key=True),
    )
    ingrediente_id: int = Field(
        sa_column=Column(ForeignKey("ingredientes.id", ondelete="RESTRICT"), primary_key=True),
    )
    es_removible: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, default=False),
    )
    es_opcional: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, default=False),
    )
    cantidad_requerida: Decimal = Field(
        default=Decimal("1.00"),
        sa_column=Column(Numeric(10, 2), nullable=False, default=1),
    )

    producto: "Producto" = Relationship(back_populates="productos_ingrediente")
    ingrediente: "Ingrediente" = Relationship(back_populates="productos_ingrediente")


if TYPE_CHECKING:
    from app.modules.ingrediente.models import Ingrediente
    from app.modules.producto.models import Producto
