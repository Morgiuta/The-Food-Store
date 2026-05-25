from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CHAR,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlmodel import Field, Relationship, SQLModel

from app.core.base_model import utcnow


class Rol(SQLModel, table=True):
    __tablename__ = "roles"

    codigo: str = Field(
        sa_column=Column(String(20), primary_key=True),
    )
    nombre: str = Field(sa_column=Column(String(50), nullable=False))
    descripcion: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    usuarios: list["UsuarioRol"] = Relationship(back_populates="rol")


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    nombre: str = Field(sa_column=Column(String(80), nullable=False))
    apellido: str = Field(sa_column=Column(String(80), nullable=False))
    email: str = Field(
        sa_column=Column(String(254), nullable=False, unique=True),
    )
    celular: str | None = Field(
        default=None,
        sa_column=Column(String(20), nullable=True),
    )
    password_hash: str = Field(sa_column=Column(CHAR(60), nullable=False))
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    @property
    def username(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.nombre} {self.apellido}".strip()

    @property
    def hashed_password(self) -> str:
        return self.password_hash

    @property
    def is_active(self) -> bool:
        return self.deleted_at is None

    roles: list["UsuarioRol"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={
            "foreign_keys": "[UsuarioRol.usuario_id]",
        },
    )
    roles_asignados: list["UsuarioRol"] = Relationship(
        back_populates="asignado_por",
        sa_relationship_kwargs={
            "foreign_keys": "[UsuarioRol.asignado_por_id]",
        },
    )
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="usuario")
    direcciones_entrega: list["DireccionEntrega"] = Relationship(back_populates="usuario")
    pedidos: list["Pedido"] = Relationship(back_populates="usuario")
    historial_pedidos: list["HistorialEstadoPedido"] = Relationship(back_populates="usuario")
    direcciones: list["Direccion"] = Relationship(back_populates="usuario")


class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_roles"

    usuario_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("usuarios.id"), primary_key=True),
    )
    rol_codigo: str = Field(
        sa_column=Column(String(20), ForeignKey("roles.codigo"), primary_key=True),
    )
    asignado_por_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, ForeignKey("usuarios.id"), nullable=True),
    )
    expires_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    usuario: Usuario = Relationship(
        back_populates="roles",
        sa_relationship_kwargs={
            "foreign_keys": "[UsuarioRol.usuario_id]",
        },
    )
    rol: Rol = Relationship(back_populates="usuarios")
    asignado_por: Usuario | None = Relationship(
        back_populates="roles_asignados",
        sa_relationship_kwargs={
            "foreign_keys": "[UsuarioRol.asignado_por_id]",
        },
    )


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    usuario_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("usuarios.id"), nullable=False),
    )
    token_hash: str = Field(
        sa_column=Column(CHAR(64), nullable=False, unique=True),
    )
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    revoked_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    usuario: Usuario = Relationship(back_populates="refresh_tokens")


class DireccionEntrega(SQLModel, table=True):
    __tablename__ = "direcciones_entrega"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    usuario_id: int = Field(
        sa_column=Column(BigInteger, ForeignKey("usuarios.id"), nullable=False),
    )
    alias: str | None = Field(default=None, sa_column=Column(String(50)))
    linea1: str = Field(sa_column=Column(Text, nullable=False))
    linea2: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    ciudad: str = Field(sa_column=Column(String(100), nullable=False))
    provincia: str | None = Field(
        default=None,
        sa_column=Column(String(100), nullable=True),
    )
    codigo_postal: str | None = Field(
        default=None,
        sa_column=Column(String(10), nullable=True),
    )
    latitud: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(9, 6), nullable=True),
    )
    longitud: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(9, 6), nullable=True),
    )
    es_principal: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, default=False),
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    usuario: Usuario = Relationship(back_populates="direcciones_entrega")


User = Usuario
Role = Rol
UserRole = UsuarioRol


if TYPE_CHECKING:
    from app.modules.direcciones.models import Direccion
    from app.modules.ventas.models import HistorialEstadoPedido, Pedido
