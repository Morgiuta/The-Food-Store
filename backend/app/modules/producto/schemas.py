from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel

from app.shared.schemas.base import PublicSchema
from app.shared.schemas.pagination import PaginatedResponse


class ProductoCategoriaLink(SQLModel):
    categoria_id: int
    es_principal: bool = False


class ProductoIngredienteLink(SQLModel):
    ingrediente_id: int
    es_removible: bool = False
    es_opcional: bool = False


class ProductoCreate(SQLModel):
    nombre: str = Field(min_length=1, max_length=150)
    descripcion: Optional[str] = None
    precio_base: Decimal = Field(ge=0)
    imagen_url: Optional[str] = None
    imagenes_url: list[str] = Field(default_factory=list)
    stock_cantidad: int = Field(default=0, ge=0)
    tiempo_prep_min: Optional[int] = Field(default=None, ge=0)
    categorias: list[ProductoCategoriaLink] = Field(default_factory=list)
    ingredientes: list[ProductoIngredienteLink] = Field(default_factory=list)


class ProductoUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=150)
    descripcion: Optional[str] = None
    precio_base: Optional[Decimal] = Field(default=None, ge=0)
    imagen_url: Optional[str] = None
    imagenes_url: Optional[list[str]] = None
    stock_cantidad: Optional[int] = Field(default=None, ge=0)
    tiempo_prep_min: Optional[int] = Field(default=None, ge=0)
    disponible: Optional[bool] = None
    categorias: Optional[list[ProductoCategoriaLink]] = None
    ingredientes: Optional[list[ProductoIngredienteLink]] = None


class ProductoPublic(PublicSchema):
    id: int
    nombre: str
    descripcion: Optional[str]
    precio_base: Decimal
    imagen_url: Optional[str]
    imagenes_url: list[str]
    stock_cantidad: int
    tiempo_prep_min: Optional[int]
    disponible: bool
    categorias: list[ProductoCategoriaLink]
    ingredientes: list[ProductoIngredienteLink]


class ProductoList(PaginatedResponse[ProductoPublic]):
    pass
