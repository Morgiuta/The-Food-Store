from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.shared.schemas.base import PublicSchema
from app.shared.schemas.pagination import PaginatedResponse


class UnidadMedidaCreate(SQLModel):
    codigo: str = Field(min_length=1, max_length=20)
    nombre: str = Field(min_length=1, max_length=80)
    simbolo: str = Field(min_length=1, max_length=20)
    descripcion: Optional[str] = None


class UnidadMedidaUpdate(SQLModel):
    codigo: Optional[str] = Field(default=None, min_length=1, max_length=20)
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=80)
    simbolo: Optional[str] = Field(default=None, min_length=1, max_length=20)
    descripcion: Optional[str] = None


class UnidadMedidaPublic(PublicSchema):
    id: int
    codigo: str
    nombre: str
    simbolo: str
    descripcion: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class UnidadMedidaList(PaginatedResponse[UnidadMedidaPublic]):
    pass
