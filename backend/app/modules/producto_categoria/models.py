from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import utcnow


class ProductoCategoria(SQLModel, table=True):
    __tablename__ = "producto_categoria"

    producto_id: int = Field(
        sa_column=Column(ForeignKey("productos.id", ondelete="CASCADE"), primary_key=True),
    )
    categoria_id: int = Field(
        sa_column=Column(ForeignKey("categorias.id", ondelete="RESTRICT"), primary_key=True),
    )
    es_principal: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, default=False),
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    producto: "Producto" = Relationship(back_populates="productos_categoria")
    categoria: "Categoria" = Relationship(back_populates="productos_categoria")


if TYPE_CHECKING:
    from app.modules.categoria.models import Categoria
    from app.modules.producto.models import Producto
