from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.core.base_model import TimestampedModel


class User(TimestampedModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    full_name: str = Field(max_length=100)
    role: str = Field(default="STOCK", max_length=20)
    hashed_password: str
    is_active: bool = True


class Role(TimestampedModel, table=True):
    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class Permission(TimestampedModel, table=True):
    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("resource", "action", name="uq_permissions_resource_action"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    resource: str = Field(index=True, max_length=50)
    action: str = Field(index=True, max_length=50)
    description: str | None = Field(default=None, max_length=255)


class RolePermission(SQLModel, table=True):
    __tablename__ = "role_permissions"

    role_id: int = Field(foreign_key="roles.id", primary_key=True)
    permission_id: int = Field(foreign_key="permissions.id", primary_key=True)


class UserRole(SQLModel, table=True):
    __tablename__ = "user_roles"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    role_id: int = Field(foreign_key="roles.id", primary_key=True)
