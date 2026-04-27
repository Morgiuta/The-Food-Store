# app/modules/teams/schemas.py
#
# Schemas Pydantic de entrada y salida para el módulo teams.
from typing import Optional, List
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from app.modules.heroes.schemas import HeroPublic


# ── Entrada ───────────────────────────────────────────────────────────────────

class TeamCreate(SQLModel):
    """Body para POST /teams/"""
    name: str = Field(min_length=2, max_length=100)
    headquarters: str = Field(min_length=2, max_length=200)


class TeamUpdate(SQLModel):
    """Body para PATCH /teams/{id} — todos los campos opcionales."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    headquarters: Optional[str] = Field(default=None, min_length=2, max_length=200)
    is_active: Optional[bool] = None


# ── Salida ────────────────────────────────────────────────────────────────────

class TeamPublic(SQLModel):
    """Response model básico para GET /teams/"""
    id: int
    name: str
    headquarters: str
    is_active: bool


class TeamList(SQLModel):
    """Response model paginado para GET /teams/"""
    data: List[TeamPublic]
    total: int


class TeamWithHeroes(BaseModel):
    """
    Response model para GET /teams/{id}/heroes.
    Usa BaseModel puro (no SQLModel) para evitar conflictos del validador
    de SQLModel al anidar instancias Pydantic en la construcción del dict.
    """
    id: int
    name: str
    headquarters: str
    is_active: bool
    heroes: List[HeroPublic] = []

    model_config = {"from_attributes": True}
