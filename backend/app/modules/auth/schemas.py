from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    username: str | None = None


class UserPublic(SQLModel):
    id: int
    username: str
    full_name: str
    role: str
    is_active: bool
