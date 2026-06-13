from sqlmodel import Session, select

from app.modules.auth.models import DireccionEntrega


class DireccionesRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_active_by_usuario(self, usuario_id: int) -> list[DireccionEntrega]:
        statement = (
            select(DireccionEntrega)
            .where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.deleted_at.is_(None),
            )
            .order_by(DireccionEntrega.es_principal.desc(), DireccionEntrega.id)
        )
        return list(self.session.exec(statement).all())

    def get_active_owned(
        self,
        usuario_id: int,
        direccion_id: int,
    ) -> DireccionEntrega | None:
        statement = select(DireccionEntrega).where(
            DireccionEntrega.id == direccion_id,
            DireccionEntrega.usuario_id == usuario_id,
            DireccionEntrega.deleted_at.is_(None),
        )
        return self.session.exec(statement).first()

    def list_active_principales(self, usuario_id: int) -> list[DireccionEntrega]:
        statement = select(DireccionEntrega).where(
            DireccionEntrega.usuario_id == usuario_id,
            DireccionEntrega.deleted_at.is_(None),
            DireccionEntrega.es_principal.is_(True),
        )
        return list(self.session.exec(statement).all())

    def has_other_principal(self, usuario_id: int, direccion_id: int) -> bool:
        statement = select(DireccionEntrega).where(
            DireccionEntrega.usuario_id == usuario_id,
            DireccionEntrega.id != direccion_id,
            DireccionEntrega.deleted_at.is_(None),
            DireccionEntrega.es_principal.is_(True),
        )
        return self.session.exec(statement).first() is not None

    def add(self, direccion: DireccionEntrega) -> DireccionEntrega:
        self.session.add(direccion)
        self.session.flush()
        return direccion

    def refresh(self, direccion: DireccionEntrega) -> DireccionEntrega:
        self.session.refresh(direccion)
        return direccion
