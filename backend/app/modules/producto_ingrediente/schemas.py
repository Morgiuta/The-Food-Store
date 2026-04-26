from sqlmodel import SQLModel

from app.shared.schemas.base import PublicSchema
from app.shared.schemas.pagination import PaginatedResponse


class ProductoIngredienteCreate(SQLModel):
    producto_id: int
    ingrediente_id: int
    es_removible: bool = False
    es_opcional: bool = False


class ProductoIngredienteUpdate(SQLModel):
    es_removible: bool
    es_opcional: bool


class ProductoIngredientePublic(PublicSchema):
    producto_id: int
    ingrediente_id: int
    es_removible: bool
    es_opcional: bool


class ProductoIngredienteList(PaginatedResponse[ProductoIngredientePublic]):
    pass
