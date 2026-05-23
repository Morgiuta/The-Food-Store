from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    email: str | None = None
    roles: list[str] = []


class UserPublic(SQLModel):
    id: int
    email: str
    nombre: str
    apellido: str
    full_name: str
    role: str
    is_active: bool
