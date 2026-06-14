from sqlmodel import Session, select

from app.modules.ventas.models import Pago


class PagoRepository:
    """Acceso a datos de la entidad Pago. Sin logica de negocio."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_pedido_id(self, pedido_id: int) -> Pago | None:
        return self.session.exec(
            select(Pago)
            .where(Pago.pedido_id == pedido_id, Pago.deleted_at.is_(None))
            .order_by(Pago.created_at.desc())
        ).first()

    def get_by_external_reference(self, external_reference: str) -> Pago | None:
        return self.session.exec(
            select(Pago)
            .where(Pago.external_reference == external_reference)
            .order_by(Pago.created_at.desc())
        ).first()

    def get_by_mp_payment_id(self, mp_payment_id: int) -> Pago | None:
        return self.session.exec(
            select(Pago).where(Pago.mp_payment_id == mp_payment_id)
        ).first()

    def get_by_idempotency_key(self, idempotency_key: str) -> Pago | None:
        return self.session.exec(
            select(Pago).where(Pago.idempotency_key == idempotency_key)
        ).first()

    def create(self, pago: Pago) -> Pago:
        self.session.add(pago)
        self.session.flush()
        self.session.refresh(pago)
        return pago

    def update(self, pago: Pago) -> Pago:
        self.session.add(pago)
        self.session.flush()
        self.session.refresh(pago)
        return pago
