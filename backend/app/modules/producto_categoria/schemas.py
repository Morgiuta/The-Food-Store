from sqlmodel import SQLModel

from app.shared.schemas.base import PublicSchema
from app.shared.schemas.pagination import PaginatedResponse


class ProductoCategoriaCreate(SQLModel):
    producto_id: int
    categoria_id: int
    es_principal: bool = False


class ProductoCategoriaUpdate(SQLModel):
    es_principal: bool


class ProductoCategoriaPublic(PublicSchema):
    producto_id: int
    categoria_id: int
    es_principal: bool


class ProductoCategoriaList(PaginatedResponse[ProductoCategoriaPublic]):
    pass
