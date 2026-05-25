from sqlmodel import Session, select

from app.modules.pedidos.service import PedidosService
from app.modules.ventas.models import EstadoPedido, FormaPago
from app.modules.ventas.schemas import (
    EstadoPedidoPublic,
    FormaPagoPublic,
    PagoCreate,
    PagoPublic,
)


class VentasService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.pedidos = PedidosService(session)

    def list_formas_pago(self) -> list[FormaPagoPublic]:
        statement = select(FormaPago).order_by(FormaPago.codigo)
        return [FormaPagoPublic.model_validate(item) for item in self.session.exec(statement)]

    def list_estados(self) -> list[EstadoPedidoPublic]:
        statement = select(EstadoPedido).where(EstadoPedido.deleted_at.is_(None)).order_by(EstadoPedido.orden)
        return [EstadoPedidoPublic.model_validate(item) for item in self.session.exec(statement)]

    def register_pago(self, pedido_id: int, data: PagoCreate) -> PagoPublic:
        return self.pedidos.register_pago(pedido_id, data)
