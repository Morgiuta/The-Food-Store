# app/modules/heroes/models.py
#
# Contiene SOLO el modelo de tabla SQLModel (Hero).
# Los schemas Pydantic de entrada/salida viven en schemas.py.
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.modules.teams.models import Team


class Hero(SQLModel, table=True):
    """Tabla heroes en la base de datos."""

    __tablename__ = "heroes"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=2, max_length=100, index=True)
    alias: str = Field(min_length=2, max_length=100, unique=True)
    power_level: int = Field(ge=1, le=100)
    is_active: bool = Field(default=True)

    team_id: Optional[int] = Field(default=None, foreign_key="teams.id")
    team: Optional["Team"] = Relationship(back_populates="heroes")
