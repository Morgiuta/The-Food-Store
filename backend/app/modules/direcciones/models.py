from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String
from sqlmodel import Field, SQLModel


class Direccion(SQLModel, table=True):
    __tablename__ = "direcciones"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    usuario_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("Usuario.id"), nullable=False),
    )
    calle: str = Field(sa_column=Column(String(120), nullable=False))
    numero: str = Field(sa_column=Column(String(20), nullable=False))
    ciudad: str = Field(sa_column=Column(String(100), nullable=False))
    provincia: str = Field(sa_column=Column(String(100), nullable=False))
    codigo_postal: str = Field(sa_column=Column(String(20), nullable=False))
    es_principal: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, default=False),
    )
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
