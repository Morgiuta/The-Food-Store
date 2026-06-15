from sqlalchemy import func, literal
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
        include_deleted: bool = False,
    ) -> list[Categoria]:
        statement = select(Categoria)
        if not include_deleted:
            statement = statement.where(Categoria.deleted_at.is_(None))
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

    def get_all_active(self, include_deleted: bool = False) -> list[Categoria]:
        statement = select(Categoria)
        if not include_deleted:
            statement = statement.where(Categoria.deleted_at.is_(None))
        return list(
            self.session.exec(
                statement.order_by(Categoria.parent_id, Categoria.orden_display, Categoria.id)
            ).all()
        )

    def get_tree_rows(self, include_deleted: bool = False) -> list[Categoria]:
        if self.session.bind and self.session.bind.dialect.name in {"postgresql", "sqlite"}:
            return self._get_tree_rows_recursive_cte(include_deleted=include_deleted)
        return self.get_all_active(include_deleted=include_deleted)

    def list_descendant_ids(self, categoria_id: int) -> set[int]:
        if self.session.bind and self.session.bind.dialect.name in {"postgresql", "sqlite"}:
            return self._list_descendant_ids_recursive_cte(categoria_id)

        descendants: set[int] = set()
        pending = [categoria_id]
        while pending:
            current_id = pending.pop()
            children = self.session.exec(
                select(Categoria.id).where(
                    Categoria.parent_id == current_id,
                    Categoria.deleted_at.is_(None),
                )
            ).all()
            for child_id in children:
                if child_id is not None and child_id not in descendants:
                    descendants.add(child_id)
                    pending.append(child_id)
        return descendants

    def _list_descendant_ids_recursive_cte(self, categoria_id: int) -> set[int]:
        descendants = (
            select(Categoria.id)
            .where(
                Categoria.parent_id == categoria_id,
                Categoria.deleted_at.is_(None),
            )
            .cte(name="categoria_descendants", recursive=True)
        )
        child = Categoria.__table__.alias("child")
        descendants = descendants.union_all(
            select(child.c.id).where(
                child.c.parent_id == descendants.c.id,
                child.c.deleted_at.is_(None),
            )
        )
        return {
            int(descendant_id)
            for descendant_id in self.session.exec(select(descendants.c.id)).all()
            if descendant_id is not None
        }

    def _get_tree_rows_recursive_cte(self, include_deleted: bool = False) -> list[Categoria]:
        base = select(Categoria.id, literal(0).label("depth")).where(Categoria.parent_id.is_(None))
        if not include_deleted:
            base = base.where(Categoria.deleted_at.is_(None))

        tree = base.cte(name="categoria_tree", recursive=True)
        child = Categoria.__table__.alias("child")
        recursive = select(child.c.id, (tree.c.depth + 1).label("depth")).where(
            child.c.parent_id == tree.c.id
        )
        if not include_deleted:
            recursive = recursive.where(child.c.deleted_at.is_(None))

        tree = tree.union_all(recursive)
        statement = (
            select(Categoria)
            .join(tree, Categoria.id == tree.c.id)
            .order_by(tree.c.depth, Categoria.parent_id, Categoria.orden_display, Categoria.id)
        )
        return list(self.session.exec(statement).all())

    def count_active(
        self,
        parent_id: int | None = None,
        filter_parent: bool = False,
        include_deleted: bool = False,
    ) -> int:
        statement = select(func.count(Categoria.id))
        if not include_deleted:
            statement = statement.where(Categoria.deleted_at.is_(None))
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
