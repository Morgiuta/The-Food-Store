from sqlmodel import Session, select

from app.core.base_repository import BaseRepository
from app.modules.producto.models import Producto


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Producto)

    def get_active_by_id(self, producto_id: int) -> Producto | None:
        return self.session.exec(
            select(Producto).where(
                Producto.id == producto_id,
                Producto.deleted_at.is_(None),
            )
        ).first()

    def list_active(self, offset: int = 0, limit: int = 20) -> list[Producto]:
        return list(
            self.session.exec(
                select(Producto)
                .where(Producto.deleted_at.is_(None))
                .order_by(Producto.id)
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count_active(self) -> int:
        return len(
            self.session.exec(select(Producto).where(Producto.deleted_at.is_(None))).all()
        )
