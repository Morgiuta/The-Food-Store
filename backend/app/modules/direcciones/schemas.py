from datetime import datetime

from sqlmodel import Field, SQLModel


class DireccionCreate(SQLModel):
    alias: str | None = Field(default=None, max_length=50)
    calle: str = Field(min_length=1, max_length=120)
    numero: str = Field(min_length=1, max_length=20)
    ciudad: str = Field(min_length=1, max_length=100)
    provincia: str | None = Field(default=None, max_length=100)
    codigo_postal: str | None = Field(default=None, max_length=20)
    es_principal: bool = False


class DireccionUpdate(SQLModel):
    alias: str | None = Field(default=None, max_length=50)
    calle: str = Field(min_length=1, max_length=120)
    numero: str = Field(min_length=1, max_length=20)
    ciudad: str = Field(min_length=1, max_length=100)
    provincia: str | None = Field(default=None, max_length=100)
    codigo_postal: str | None = Field(default=None, max_length=20)
    es_principal: bool = False


class DireccionPublic(SQLModel):
    id: int
    usuario_id: int
    alias: str | None
    calle: str
    numero: str
    ciudad: str
    provincia: str | None
    codigo_postal: str | None
    es_principal: bool
    deleted_at: datetime | None
