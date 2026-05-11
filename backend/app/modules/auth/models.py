from typing import Optional

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
