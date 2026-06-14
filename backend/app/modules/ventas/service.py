from sqlmodel import Session

from app.modules.pedidos.service import PedidosService
from app.modules.ventas.repository import VentasRepository
from app.modules.ventas.schemas import (
    EstadoPedidoPublic,
    FormaPagoPublic,
)


class VentasService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.pedidos = PedidosService(session)
        self.ventas = VentasRepository(session)

    def list_formas_pago(self) -> list[FormaPagoPublic]:
        return [
            FormaPagoPublic.model_validate(item)
            for item in self.ventas.list_formas_pago()
        ]

    def list_estados(self) -> list[EstadoPedidoPublic]:
        return [
            EstadoPedidoPublic.model_validate(item)
            for item in self.ventas.list_estados_activos()
        ]
