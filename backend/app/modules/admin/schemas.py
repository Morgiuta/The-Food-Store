from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class RolPublic(SQLModel):
    codigo: str
    nombre: str


class UsuarioPublic(SQLModel):
    id: int
    nombre: str
    apellido: str
    email: str
    roles: list[RolPublic]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UsuarioList(SQLModel):
    items: list[UsuarioPublic]
    total: int
    page: int
    limit: int


class UsuarioUpdate(SQLModel):
    model_config = {"extra": "forbid"}

    nombre: Optional[str] = Field(default=None, min_length=1, max_length=80)
    email: Optional[str] = Field(default=None, min_length=3, max_length=254)


class UsuarioRolUpdate(SQLModel):
    model_config = {"extra": "forbid"}

    rol_nombre: str = Field(min_length=1, max_length=50)
