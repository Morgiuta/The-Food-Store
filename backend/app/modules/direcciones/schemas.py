from datetime import datetime

from sqlmodel import Field, SQLModel


class DireccionCreate(SQLModel):
    calle: str = Field(min_length=1, max_length=120)
    numero: str = Field(min_length=1, max_length=20)
    ciudad: str = Field(min_length=1, max_length=100)
    provincia: str = Field(min_length=1, max_length=100)
    codigo_postal: str = Field(min_length=1, max_length=20)
    es_principal: bool = False


class DireccionUpdate(SQLModel):
    calle: str = Field(min_length=1, max_length=120)
    numero: str = Field(min_length=1, max_length=20)
    ciudad: str = Field(min_length=1, max_length=100)
    provincia: str = Field(min_length=1, max_length=100)
    codigo_postal: str = Field(min_length=1, max_length=20)
    es_principal: bool = False


class DireccionPublic(SQLModel):
    id: int
    usuario_id: int
    calle: str
    numero: str
    ciudad: str
    provincia: str
    codigo_postal: str
    es_principal: bool
    deleted_at: datetime | None
