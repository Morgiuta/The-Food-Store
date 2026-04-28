from sqlmodel import Session

from app.core.unit_of_work import UnitOfWork
from app.modules.categoria.repository import CategoriaRepository
from app.modules.ingrediente.repository import IngredienteRepository
from app.modules.producto.repository import ProductoRepository
from app.modules.producto_categoria.repository import ProductoCategoriaRepository
from app.modules.producto_ingrediente.repository import ProductoIngredienteRepository


class ProductoUnitOfWork(UnitOfWork):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.productos = ProductoRepository(session)
        self.categorias = CategoriaRepository(session)
        self.ingredientes = IngredienteRepository(session)
        self.producto_categorias = ProductoCategoriaRepository(session)
        self.producto_ingredientes = ProductoIngredienteRepository(session)
