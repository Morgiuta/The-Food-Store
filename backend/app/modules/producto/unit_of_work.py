from sqlmodel import Session

from app.core.unit_of_work import UnitOfWork
from app.modules.producto.repository import ProductoRepository


class ProductoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.productos = ProductoRepository(session)
