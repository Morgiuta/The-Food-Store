from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, DateTime, String, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import utcnow


class UnidadMedida(SQLModel, table=True):
    __tablename__ = "unidades_medida"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(sa_column=Column(String(20), nullable=False))
    nombre: str = Field(sa_column=Column(String(80), nullable=False))
    simbolo: str = Field(sa_column=Column(String(20), nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
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

    productos: list["Producto"] = Relationship(back_populates="unidad_venta")

    __table_args__ = (UniqueConstraint("codigo", name="uq_unidad_medida_codigo"),)


if TYPE_CHECKING:
    from app.modules.producto.models import Producto
