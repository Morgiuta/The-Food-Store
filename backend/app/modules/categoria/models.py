from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import utcnow


class Categoria(SQLModel, table=True):
    __tablename__ = "categorias"

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(
        default=None,
        sa_column=Column(ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True),
    )
    nombre: str = Field(sa_column=Column(String(100), nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    imagen_url: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    orden_display: int = Field(default=0, nullable=False)
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

    productos_categoria: list["ProductoCategoria"] = Relationship(back_populates="categoria")

    __table_args__ = (UniqueConstraint("nombre", name="uq_categoria_nombre"),)


if TYPE_CHECKING:
    from app.modules.producto_categoria.models import ProductoCategoria
