from sqlmodel import Field, SQLModel


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


class UserRegister(SQLModel):
    nombre: str = Field(min_length=1, max_length=160)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)
