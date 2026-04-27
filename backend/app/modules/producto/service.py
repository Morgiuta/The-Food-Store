from fastapi import HTTPException, status

from app.core.base_service import BaseService
from app.core.utils import utcnow
from app.modules.producto.models import Producto
from app.modules.producto.schemas import (
    ProductoCreate,
    ProductoList,
    ProductoPublic,
    ProductoUpdate,
)
from app.modules.producto.unit_of_work import ProductoUnitOfWork


class ProductoService(BaseService):
    def _get_or_404(self, uow: ProductoUnitOfWork, producto_id: int) -> Producto:
        producto = uow.productos.get_active_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id={producto_id} no encontrado",
            )
        return producto

    def _apply_stock_rule(self, producto: Producto) -> None:
        producto.disponible = producto.stock_cantidad > 0

    def create(self, data: ProductoCreate) -> ProductoPublic:
        with ProductoUnitOfWork(self._session) as uow:
            producto = Producto.model_validate(data)
            self._apply_stock_rule(producto)
            uow.productos.add(producto)
            result = ProductoPublic.model_validate(producto)
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> ProductoList:
        with ProductoUnitOfWork(self._session) as uow:
            productos = uow.productos.list_active(offset=offset, limit=limit)
            total = uow.productos.count_active()
            result = ProductoList(
                data=[ProductoPublic.model_validate(producto) for producto in productos],
                total=total,
            )
        return result

    def get_by_id(self, producto_id: int) -> ProductoPublic:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            result = ProductoPublic.model_validate(producto)
        return result

    def update(self, producto_id: int, data: ProductoUpdate) -> ProductoPublic:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            patch = data.model_dump(exclude_unset=True)

            for field, value in patch.items():
                setattr(producto, field, value)

            self._apply_stock_rule(producto)
            producto.updated_at = utcnow()
            uow.productos.add(producto)
            result = ProductoPublic.model_validate(producto)
        return result

    def soft_delete(self, producto_id: int) -> None:
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            producto.deleted_at = utcnow()
            producto.updated_at = utcnow()
            uow.productos.add(producto)
