from fastapi import HTTPException, status

from app.core.base_service import BaseService
from app.modules.producto_ingrediente.models import ProductoIngrediente
from app.modules.producto_ingrediente.schemas import (
    ProductoIngredienteCreate,
    ProductoIngredienteList,
    ProductoIngredientePublic,
    ProductoIngredienteUpdate,
)
from app.modules.producto_ingrediente.unit_of_work import ProductoIngredienteUnitOfWork


class ProductoIngredienteService(BaseService):
    def _get_link_or_404(
        self,
        uow: ProductoIngredienteUnitOfWork,
        producto_id: int,
        ingrediente_id: int,
    ) -> ProductoIngrediente:
        link = uow.producto_ingredientes.get_link(producto_id, ingrediente_id)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Relacion producto-ingrediente no encontrada "
                    f"(producto_id={producto_id}, ingrediente_id={ingrediente_id})"
                ),
            )
        return link

    def _assert_producto_exists(self, uow: ProductoIngredienteUnitOfWork, producto_id: int) -> None:
        if not uow.productos.get_active_by_id(producto_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id={producto_id} no encontrado",
            )

    def _assert_ingrediente_exists(
        self,
        uow: ProductoIngredienteUnitOfWork,
        ingrediente_id: int,
    ) -> None:
        if not uow.ingredientes.get_by_id(ingrediente_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingrediente con id={ingrediente_id} no encontrado",
            )

    def create(self, data: ProductoIngredienteCreate) -> ProductoIngredientePublic:
        with ProductoIngredienteUnitOfWork(self._session) as uow:
            self._assert_producto_exists(uow, data.producto_id)
            self._assert_ingrediente_exists(uow, data.ingrediente_id)
            if uow.producto_ingredientes.get_link(data.producto_id, data.ingrediente_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="La relacion producto-ingrediente ya existe",
                )
            link = ProductoIngrediente.model_validate(data)
            uow.producto_ingredientes.add(link)
            result = ProductoIngredientePublic.model_validate(link)
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> ProductoIngredienteList:
        with ProductoIngredienteUnitOfWork(self._session) as uow:
            links = uow.producto_ingredientes.list_all(offset=offset, limit=limit)
            total = uow.producto_ingredientes.count_all()
            result = ProductoIngredienteList(
                data=[ProductoIngredientePublic.model_validate(link) for link in links],
                total=total,
            )
        return result

    def get_by_id(self, producto_id: int, ingrediente_id: int) -> ProductoIngredientePublic:
        with ProductoIngredienteUnitOfWork(self._session) as uow:
            link = self._get_link_or_404(uow, producto_id, ingrediente_id)
            result = ProductoIngredientePublic.model_validate(link)
        return result

    def update(
        self,
        producto_id: int,
        ingrediente_id: int,
        data: ProductoIngredienteUpdate,
    ) -> ProductoIngredientePublic:
        with ProductoIngredienteUnitOfWork(self._session) as uow:
            link = self._get_link_or_404(uow, producto_id, ingrediente_id)
            link.es_removible = data.es_removible
            link.es_opcional = data.es_opcional
            uow.producto_ingredientes.add(link)
            result = ProductoIngredientePublic.model_validate(link)
        return result

    def delete(self, producto_id: int, ingrediente_id: int) -> None:
        with ProductoIngredienteUnitOfWork(self._session) as uow:
            link = self._get_link_or_404(uow, producto_id, ingrediente_id)
            uow.producto_ingredientes.session.delete(link)
            uow.producto_ingredientes.session.flush()
