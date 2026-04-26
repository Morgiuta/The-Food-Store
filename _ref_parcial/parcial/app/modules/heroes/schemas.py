# app/modules/heroes/schemas.py
#
# Schemas Pydantic de entrada y salida para el módulo heroes.
# Separados del modelo de tabla para respetar el principio de
# responsabilidad única: models.py define la DB, schemas.py define
# los contratos HTTP.
from typing import Optional, List
from sqlmodel import SQLModel, Field


# ── Entrada ───────────────────────────────────────────────────────────────────

class HeroCreate(SQLModel):
    """Body para POST /heroes/"""
    name: str = Field(min_length=2, max_length=100)
    alias: str = Field(min_length=2, max_length=100)
    power_level: int = Field(ge=1, le=100)
    team_id: Optional[int] = None


class HeroUpdate(SQLModel):
    """Body para PATCH /heroes/{id} — todos los campos opcionales."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    alias: Optional[str] = Field(default=None, min_length=2, max_length=100)
    power_level: Optional[int] = Field(default=None, ge=1, le=100)
    team_id: Optional[int] = None
    is_active: Optional[bool] = None


# ── Salida ────────────────────────────────────────────────────────────────────

class HeroPublic(SQLModel):
    """Response model: campos que se exponen al cliente."""
    id: int
    name: str
    alias: str
    power_level: int
    is_active: bool
    team_id: Optional[int] = None


class HeroList(SQLModel):
    """Response model paginado para GET /heroes/"""
    data: List[HeroPublic]
    total: int
