from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.core.base_repository import BaseRepository
from app.modules.ingrediente.models import Ingrediente
from app.modules.ingrediente.schemas import IngredienteListParams


class IngredienteRepository(BaseRepository[Ingrediente]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Ingrediente)

    def get_by_id(self, record_id: int, include_deleted: bool = False) -> Ingrediente | None:
        statement = select(Ingrediente).where(Ingrediente.id == record_id)
        if not include_deleted:
            statement = statement.where(Ingrediente.deleted_at.is_(None))
        return self.session.exec(statement).first()

    def get_by_nombre(self, nombre: str, include_deleted: bool = False) -> Ingrediente | None:
        statement = select(Ingrediente).where(
            func.lower(Ingrediente.nombre) == nombre.strip().lower()
        )
        if not include_deleted:
            statement = statement.where(Ingrediente.deleted_at.is_(None))
        return self.session.exec(
            statement
        ).first()

    def list_by_ids(
        self,
        ingrediente_ids: list[int],
        include_deleted: bool = False,
    ) -> list[Ingrediente]:
        if not ingrediente_ids:
            return []

        statement = select(Ingrediente).where(Ingrediente.id.in_(ingrediente_ids))
        if not include_deleted:
            statement = statement.where(Ingrediente.deleted_at.is_(None))

        return list(self.session.exec(statement.order_by(Ingrediente.id)).all())

    def _apply_filters(self, statement, params: IngredienteListParams):
        if not params.include_deleted:
            statement = statement.where(Ingrediente.deleted_at.is_(None))

        if params.es_alergeno is not None:
            statement = statement.where(Ingrediente.es_alergeno == params.es_alergeno)

        if params.search:
            term = f"%{params.search.strip().lower()}%"
            statement = statement.where(
                or_(
                    func.lower(Ingrediente.nombre).like(term),
                    func.lower(func.coalesce(Ingrediente.descripcion, "")).like(term),
                )
            )

        return statement

    def list_all(self, params: IngredienteListParams) -> list[Ingrediente]:
        sort_column = getattr(Ingrediente, params.sort_by)
        if params.sort_dir == "desc":
            sort_column = sort_column.desc()

        return list(
            self.session.exec(
                self._apply_filters(select(Ingrediente), params)
                .order_by(sort_column, Ingrediente.id)
                .offset(params.offset)
                .limit(params.limit)
            ).all()
        )

    def count_all(self, params: IngredienteListParams) -> int:
        statement = self._apply_filters(select(func.count(Ingrediente.id)), params)
        return self.session.exec(statement).one()
