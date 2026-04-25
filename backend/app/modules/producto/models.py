from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Text, Numeric, Integer, Boolean, DateTime, CheckConstraint

if TYPE_CHECKING:
  from .producto_categoria.models import ProductoCategoria
  from .producto_ingrediente.models import ProductoIngrediente

class Producto(SQLModel, table=True):
    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)

    nombre: str = Field(sa_column=Column(String(150), nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    precio_base: float = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    imagen_url: Optional[str] = Field(default=None, sa_column=Column(Text))
    stock_cantidad: int = Field(default=0, sa_column=Column(Integer, nullable=False, default=0))
    disponible: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, default=True))

    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))

    # Relaciones (se completan después)
    categorias: List["Categoria"] = Relationship(back_populates="productos")
    ingredientes: List["Ingrediente"] = Relationship(back_populates="productos")

    __table_args__ = (
        CheckConstraint("precio_base >= 0", name="check_precio_base_positive"),
        CheckConstraint("stock_cantidad >= 0", name="check_stock_cantidad_positive"),
    )
    
    categorias: List["Categoria"] = Relationship(
      back_populates="productos",
      link_model=ProductoCategoria
    )

    ingredientes: List["Ingrediente"] = Relationship(
        back_populates="productos",
        link_model=ProductoIngrediente
    )