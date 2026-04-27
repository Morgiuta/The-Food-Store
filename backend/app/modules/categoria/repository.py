from sqlmodel import Session, select

from app.core.base_repository import BaseRepository
from app.modules.categoria.models import Categoria


class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Categoria)

    def get_active_by_id(self, categoria_id: int) -> Categoria | None:
        return self.session.exec(
            select(Categoria).where(
                Categoria.id == categoria_id,
                Categoria.deleted_at.is_(None),
            )
        ).first()

    def get_by_nombre(self, nombre: str) -> Categoria | None:
        return self.session.exec(
            select(Categoria).where(
                Categoria.nombre == nombre,
                Categoria.deleted_at.is_(None),
            )
        ).first()

    def list_active(self, offset: int = 0, limit: int = 20) -> list[Categoria]:
        return list(
            self.session.exec(
                select(Categoria)
                .where(Categoria.deleted_at.is_(None))
                .order_by(Categoria.orden_display, Categoria.id)
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count_active(self) -> int:
        return len(
            self.session.exec(
                select(Categoria).where(Categoria.deleted_at.is_(None))
            ).all()
        )
