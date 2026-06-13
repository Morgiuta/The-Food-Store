from sqlmodel import Field, SQLModel

from app.modules.ventas.schemas import PedidoPublic
from app.shared.schemas.pagination import PaginatedResponse


class PedidoEstadoPatch(SQLModel):
    nuevo_estado: str = Field(min_length=1, max_length=20)


class PedidoList(PaginatedResponse[PedidoPublic]):
    pass
