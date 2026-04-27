from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, String, Text, UniqueConstraint
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
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    productos_ingrediente: list["ProductoIngrediente"] = Relationship(
        back_populates="ingrediente"
    )

    __table_args__ = (UniqueConstraint("nombre", name="uq_ingrediente_nombre"),)


if TYPE_CHECKING:
    from app.modules.producto_ingrediente.models import ProductoIngrediente
