from sqlmodel import Session

from app.core.unit_of_work import UnitOfWork
from app.modules.ingrediente.repository import IngredienteRepository
from app.modules.producto.repository import ProductoRepository
from app.modules.producto_ingrediente.repository import ProductoIngredienteRepository


class ProductoIngredienteUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.producto_ingredientes = ProductoIngredienteRepository(session)
        self.productos = ProductoRepository(session)
        self.ingredientes = IngredienteRepository(session)
