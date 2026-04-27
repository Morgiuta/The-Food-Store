# app/modules/teams/models.py
#
# Contiene SOLO el modelo de tabla SQLModel (Team).
# Los schemas Pydantic de entrada/salida viven en schemas.py.
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.modules.heroes.models import Hero


class Team(SQLModel, table=True):
    """Tabla teams en la base de datos."""

    __tablename__ = "teams"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=2, max_length=100, unique=True, index=True)
    headquarters: str = Field(min_length=2, max_length=200)
    is_active: bool = Field(default=True)

    heroes: List["Hero"] = Relationship(back_populates="team")
