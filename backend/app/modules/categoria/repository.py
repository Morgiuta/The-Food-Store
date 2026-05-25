from sqlalchemy import func
from sqlmodel import Session, select

from app.core.base_repository import BaseRepository
from app.modules.categoria.models import Categoria
from app.modules.producto.models import Producto
from app.modules.producto_categoria.models import ProductoCategoria


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

    def list_active(
        self,
        offset: int = 0,
        limit: int = 20,
        parent_id: int | None = None,
        filter_parent: bool = False,
    ) -> list[Categoria]:
        statement = select(Categoria).where(Categoria.deleted_at.is_(None))
        if filter_parent:
            if parent_id is None:
                statement = statement.where(Categoria.parent_id.is_(None))
            else:
                statement = statement.where(Categoria.parent_id == parent_id)

        return list(
            self.session.exec(
                statement.order_by(Categoria.orden_display, Categoria.id)
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def get_all_active(self) -> list[Categoria]:
        statement = select(Categoria).where(Categoria.deleted_at.is_(None))
        return list(
            self.session.exec(
                statement.order_by(Categoria.parent_id, Categoria.orden_display, Categoria.id)
            ).all()
        )

    def count_active(
        self,
        parent_id: int | None = None,
        filter_parent: bool = False,
    ) -> int:
        statement = select(func.count(Categoria.id)).where(Categoria.deleted_at.is_(None))
        if filter_parent:
            if parent_id is None:
                statement = statement.where(Categoria.parent_id.is_(None))
            else:
                statement = statement.where(Categoria.parent_id == parent_id)

        return int(self.session.exec(statement).one())

    def has_active_products(self, categoria_id: int) -> bool:
        statement = (
            select(Producto.id)
            .join(ProductoCategoria, ProductoCategoria.producto_id == Producto.id)
            .where(
                ProductoCategoria.categoria_id == categoria_id,
                Producto.deleted_at.is_(None),
            )
            .limit(1)
        )
        return self.session.exec(statement).first() is not None
