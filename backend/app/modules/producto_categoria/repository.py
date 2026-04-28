from sqlmodel import Session, select

from app.core.base_repository import BaseRepository
from app.modules.producto_categoria.models import ProductoCategoria


class ProductoCategoriaRepository(BaseRepository[ProductoCategoria]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, ProductoCategoria)

    def get_link(self, producto_id: int, categoria_id: int) -> ProductoCategoria | None:
        return self.session.get(ProductoCategoria, (producto_id, categoria_id))

    def list_all(self, offset: int = 0, limit: int = 20) -> list[ProductoCategoria]:
        return list(
            self.session.exec(
                select(ProductoCategoria)
                .order_by(ProductoCategoria.producto_id, ProductoCategoria.categoria_id)
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count_all(self) -> int:
        return len(self.session.exec(select(ProductoCategoria)).all())

    def list_by_producto(self, producto_id: int) -> list[ProductoCategoria]:
        return list(
            self.session.exec(
                select(ProductoCategoria)
                .where(ProductoCategoria.producto_id == producto_id)
                .order_by(ProductoCategoria.categoria_id)
            ).all()
        )

    def list_by_producto_ids(self, producto_ids: list[int]) -> list[ProductoCategoria]:
        if not producto_ids:
            return []
        return list(
            self.session.exec(
                select(ProductoCategoria)
                .where(ProductoCategoria.producto_id.in_(producto_ids))
                .order_by(ProductoCategoria.producto_id, ProductoCategoria.categoria_id)
            ).all()
        )

    def get_principal_for_producto(self, producto_id: int) -> ProductoCategoria | None:
        return self.session.exec(
            select(ProductoCategoria).where(
                ProductoCategoria.producto_id == producto_id,
                ProductoCategoria.es_principal == True,  # noqa: E712
            )
        ).first()
