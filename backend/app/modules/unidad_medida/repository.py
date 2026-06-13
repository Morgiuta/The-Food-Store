from sqlalchemy import func
from sqlmodel import Session, select

from app.core.base_repository import BaseRepository
from app.modules.unidad_medida.models import UnidadMedida


class UnidadMedidaRepository(BaseRepository[UnidadMedida]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, UnidadMedida)

    def get_active_by_id(self, unidad_id: int) -> UnidadMedida | None:
        return self.session.exec(
            select(UnidadMedida).where(
                UnidadMedida.id == unidad_id,
                UnidadMedida.deleted_at.is_(None),
            )
        ).first()

    def get_active_by_codigo(self, codigo: str) -> UnidadMedida | None:
        return self.session.exec(
            select(UnidadMedida).where(
                UnidadMedida.codigo == codigo,
                UnidadMedida.deleted_at.is_(None),
            )
        ).first()

    def list_active(self, offset: int = 0, limit: int = 100) -> list[UnidadMedida]:
        return list(
            self.session.exec(
                select(UnidadMedida)
                .where(UnidadMedida.deleted_at.is_(None))
                .order_by(UnidadMedida.id)
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count_active(self) -> int:
        return int(
            self.session.exec(
                select(func.count(UnidadMedida.id)).where(
                    UnidadMedida.deleted_at.is_(None)
                )
            ).one()
        )

    def list_by_ids(self, unidad_ids: list[int]) -> list[UnidadMedida]:
        if not unidad_ids:
            return []
        return list(
            self.session.exec(
                select(UnidadMedida).where(UnidadMedida.id.in_(unidad_ids))
            ).all()
        )
