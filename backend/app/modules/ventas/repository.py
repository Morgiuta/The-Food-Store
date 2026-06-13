from sqlmodel import Session, select

from app.modules.ventas.models import EstadoPedido, FormaPago


class VentasRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_formas_pago(self) -> list[FormaPago]:
        statement = select(FormaPago).order_by(FormaPago.codigo)
        return list(self.session.exec(statement).all())

    def list_estados_activos(self) -> list[EstadoPedido]:
        statement = (
            select(EstadoPedido)
            .where(EstadoPedido.deleted_at.is_(None))
            .order_by(EstadoPedido.orden)
        )
        return list(self.session.exec(statement).all())
