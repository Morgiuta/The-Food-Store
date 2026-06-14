from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.shared.schemas.pagination import PaginatedResponse


class RolPublic(SQLModel):
    codigo: str
    nombre: str
    expires_at: Optional[datetime] = None


class UsuarioPublic(SQLModel):
    id: int
    nombre: str
    apellido: str
    email: str
    roles: list[RolPublic]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UsuarioList(PaginatedResponse[UsuarioPublic]):
    pass


class UsuarioCreate(SQLModel):
    model_config = {"extra": "forbid"}

    nombre: str = Field(min_length=1, max_length=80)
    apellido: str = Field(min_length=1, max_length=80)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    celular: Optional[str] = Field(default=None, max_length=20)
    rol_nombre: str = Field(default="CLIENT", min_length=1, max_length=50)
    rol_expires_at: Optional[datetime] = None


class UsuarioUpdate(SQLModel):
    model_config = {"extra": "forbid"}

    nombre: Optional[str] = Field(default=None, min_length=1, max_length=80)
    apellido: Optional[str] = Field(default=None, min_length=1, max_length=80)
    email: Optional[str] = Field(default=None, min_length=3, max_length=254)
    celular: Optional[str] = Field(default=None, max_length=20)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)


class UsuarioRolUpdate(SQLModel):
    model_config = {"extra": "forbid"}

    rol_nombre: str = Field(min_length=1, max_length=50)
    expires_at: Optional[datetime] = None
