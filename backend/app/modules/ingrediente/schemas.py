from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from sqlmodel import Field, SQLModel

from app.shared.schemas.base import PublicSchema
from app.shared.schemas.pagination import PaginatedResponse


UnidadIngrediente = Literal["unidad", "kg", "litros", "gramos", "ml"]


class IngredienteCreate(SQLModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: Optional[str] = None
    es_alergeno: bool = False
    stock_actual: Decimal = Field(default=Decimal("0.00"), ge=0)
    unidad: UnidadIngrediente = "unidad"
    es_producto_terminado: bool = False


class IngredienteUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    es_alergeno: Optional[bool] = None
    stock_actual: Optional[Decimal] = Field(default=None, ge=0)
    unidad: UnidadIngrediente = "unidad"
    es_producto_terminado: bool = False


class IngredientePublic(PublicSchema):
    id: int
    nombre: str
    descripcion: Optional[str]
    es_alergeno: bool
    stock_actual: Decimal
    unidad: UnidadIngrediente = "unidad"
    es_producto_terminado: bool = False
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class IngredienteListParams(SQLModel):
    search: Optional[str] = Field(default=None, max_length=100)
    es_alergeno: Optional[bool] = None
    include_deleted: bool = False
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
    sort_by: Literal["id", "nombre", "es_alergeno", "created_at", "updated_at"] = "nombre"
    sort_dir: Literal["asc", "desc"] = "asc"


class IngredienteList(PaginatedResponse[IngredientePublic]):
    pass
