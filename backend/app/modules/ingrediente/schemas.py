from typing import Optional

from sqlmodel import Field, SQLModel

from app.shared.schemas.base import PublicSchema
from app.shared.schemas.pagination import PaginatedResponse


class IngredienteCreate(SQLModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: Optional[str] = None
    es_alergeno: bool = False


class IngredienteUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None


class IngredientePublic(PublicSchema):
    id: int
    nombre: str
    descripcion: Optional[str]
    es_alergeno: bool


class IngredienteList(PaginatedResponse[IngredientePublic]):
    pass
