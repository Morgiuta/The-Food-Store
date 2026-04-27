from sqlmodel import Session, select

from app.core.base_repository import BaseRepository
from app.modules.ingrediente.models import Ingrediente


class IngredienteRepository(BaseRepository[Ingrediente]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Ingrediente)

    def get_by_nombre(self, nombre: str) -> Ingrediente | None:
        return self.session.exec(
            select(Ingrediente).where(Ingrediente.nombre == nombre)
        ).first()

    def list_all(self, offset: int = 0, limit: int = 20) -> list[Ingrediente]:
        return list(
            self.session.exec(
                select(Ingrediente)
                .order_by(Ingrediente.id)
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count_all(self) -> int:
        return len(self.session.exec(select(Ingrediente)).all())
