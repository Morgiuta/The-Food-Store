from sqlmodel import Session, select

from app.core.base_repository import BaseRepository
from app.modules.producto_ingrediente.models import ProductoIngrediente


class ProductoIngredienteRepository(BaseRepository[ProductoIngrediente]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, ProductoIngrediente)

    def get_link(self, producto_id: int, ingrediente_id: int) -> ProductoIngrediente | None:
        return self.session.get(ProductoIngrediente, (producto_id, ingrediente_id))

    def list_all(self, offset: int = 0, limit: int = 20) -> list[ProductoIngrediente]:
        return list(
            self.session.exec(
                select(ProductoIngrediente)
                .order_by(ProductoIngrediente.producto_id, ProductoIngrediente.ingrediente_id)
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count_all(self) -> int:
        return len(self.session.exec(select(ProductoIngrediente)).all())
