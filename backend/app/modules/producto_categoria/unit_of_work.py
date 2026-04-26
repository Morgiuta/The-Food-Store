from sqlmodel import Session

from app.core.unit_of_work import UnitOfWork
from app.modules.categoria.repository import CategoriaRepository
from app.modules.producto.repository import ProductoRepository
from app.modules.producto_categoria.repository import ProductoCategoriaRepository


class ProductoCategoriaUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.producto_categorias = ProductoCategoriaRepository(session)
        self.productos = ProductoRepository(session)
        self.categorias = CategoriaRepository(session)
