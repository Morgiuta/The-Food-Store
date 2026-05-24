from sqlmodel import Field, SQLModel

from app.modules.ventas.schemas import PedidoPublic


class PedidoEstadoPatch(SQLModel):
    nuevo_estado: str = Field(min_length=1, max_length=20)


class PedidoList(SQLModel):
    items: list[PedidoPublic]
    total: int
    page: int
    limit: int
