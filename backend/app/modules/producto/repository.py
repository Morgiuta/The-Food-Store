from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.core.base_repository import BaseRepository
from app.modules.producto.models import Producto
from app.modules.producto_categoria.models import ProductoCategoria


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

    def _apply_public_filters(
        self,
        statement,
        categoria_id: int | None = None,
        disponible: bool | None = None,
        q: str | None = None,
    ):
        statement = statement.where(Producto.deleted_at.is_(None))

        if categoria_id is not None:
            statement = statement.join(
                ProductoCategoria,
                ProductoCategoria.producto_id == Producto.id,
            ).where(ProductoCategoria.categoria_id == categoria_id)

        if disponible is not None:
            statement = statement.where(Producto.disponible == disponible)

        if q and q.strip():
            term = f"%{q.strip()}%"
            statement = statement.where(
                or_(
                    Producto.nombre.ilike(term),
                    Producto.descripcion.ilike(term),
                )
            )

        return statement

    def list_active(
        self,
        offset: int = 0,
        limit: int = 20,
        categoria_id: int | None = None,
        disponible: bool | None = None,
        q: str | None = None,
    ) -> list[Producto]:
        statement = self._apply_public_filters(
            select(Producto),
            categoria_id=categoria_id,
            disponible=disponible,
            q=q,
        )
        return list(
            self.session.exec(statement.order_by(Producto.id).offset(offset).limit(limit)).all()
        )

    def count_active(
        self,
        categoria_id: int | None = None,
        disponible: bool | None = None,
        q: str | None = None,
    ) -> int:
        statement = self._apply_public_filters(
            select(func.count(func.distinct(Producto.id))),
            categoria_id=categoria_id,
            disponible=disponible,
            q=q,
        )
        return int(self.session.exec(statement).one())
