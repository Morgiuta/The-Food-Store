from typing import Optional

from sqlmodel import Field, SQLModel

from app.shared.schemas.base import PublicSchema
from app.shared.schemas.pagination import PaginatedResponse


class CategoriaCreate(SQLModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None
    orden_display: int = Field(default=0, ge=0)


class CategoriaUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None
    orden_display: Optional[int] = Field(default=None, ge=0)


class CategoriaPublic(PublicSchema):
    id: int
    parent_id: Optional[int]
    nombre: str
    descripcion: Optional[str]
    imagen_url: Optional[str]
    orden_display: int


class CategoriaList(PaginatedResponse[CategoriaPublic]):
    pass
