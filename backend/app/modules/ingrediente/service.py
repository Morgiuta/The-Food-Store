from fastapi import HTTPException, status

from app.core.base_service import BaseService
from app.core.utils import utcnow
from app.modules.ingrediente.models import Ingrediente
from app.modules.ingrediente.schemas import (
    IngredienteCreate,
    IngredienteList,
    IngredienteListParams,
    IngredientePublic,
    IngredienteUpdate,
)
from app.modules.ingrediente.unit_of_work import IngredienteUnitOfWork
from app.modules.producto.service import ProductoService
from app.modules.producto.unit_of_work import ProductoUnitOfWork


class IngredienteService(BaseService):
    def _get_or_404(self, uow: IngredienteUnitOfWork, ingrediente_id: int) -> Ingrediente:
        ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingrediente con id={ingrediente_id} no encontrado",
            )
        return ingrediente

    def _assert_nombre_unique(
        self,
        uow: IngredienteUnitOfWork,
        nombre: str,
        current_id: int | None = None,
    ) -> None:
        ingrediente = uow.ingredientes.get_by_nombre(nombre, include_deleted=True)
        if ingrediente and ingrediente.id != current_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un ingrediente con nombre '{nombre}'",
            )

    def create(self, data: IngredienteCreate) -> IngredientePublic:
        with IngredienteUnitOfWork(self._session) as uow:
            self._assert_nombre_unique(uow, data.nombre)
            ingrediente = Ingrediente.model_validate(data)
            uow.ingredientes.add(ingrediente)
            result = IngredientePublic.model_validate(ingrediente)
        return result

    def get_all(self, params: IngredienteListParams) -> IngredienteList:
        with IngredienteUnitOfWork(self._session) as uow:
            ingredientes = uow.ingredientes.list_all(params)
            total = uow.ingredientes.count_all(params)
            result = IngredienteList(
                data=[IngredientePublic.model_validate(ingrediente) for ingrediente in ingredientes],
                total=total,
            )
        return result

    def get_by_id(self, ingrediente_id: int) -> IngredientePublic:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            result = IngredientePublic.model_validate(ingrediente)
        return result

    def update(self, ingrediente_id: int, data: IngredienteUpdate) -> IngredientePublic:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            if ingrediente.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="No se puede editar un ingrediente inactivo",
                )
            patch = data.model_dump(exclude_unset=True)

            if "nombre" in patch:
                self._assert_nombre_unique(uow, patch["nombre"], current_id=ingrediente.id)

            for field, value in patch.items():
                setattr(ingrediente, field, value)

            ingrediente.updated_at = utcnow()
            uow.ingredientes.add(ingrediente)
            uow.ingredientes.session.flush()

            if "stock_actual" in patch:
                with ProductoUnitOfWork(self._session) as prod_uow:
                    prod_svc = ProductoService(self._session)
                    links = prod_uow.producto_ingredientes.list_by_ingrediente(ingrediente.id)
                    producto_ids = list(set(link.producto_id for link in links))
                    for pid in producto_ids:
                        producto = prod_uow.productos.get_active_by_id(pid)
                        if producto:
                            prod_svc.recalcular_stock(prod_uow, producto)
                            prod_uow.productos.add(producto)
                    prod_uow.productos.session.flush()

            result = IngredientePublic.model_validate(ingrediente)
        return result

    def restore(self, ingrediente_id: int) -> IngredientePublic:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = uow.ingredientes.get_by_id(ingrediente_id, include_deleted=True)
            if not ingrediente:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ingrediente con id={ingrediente_id} no encontrado",
                )
            ingrediente.deleted_at = None
            ingrediente.updated_at = utcnow()
            uow.ingredientes.add(ingrediente)
            result = IngredientePublic.model_validate(ingrediente)
        return result

    def delete(self, ingrediente_id: int) -> None:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            ingrediente.deleted_at = utcnow()
            ingrediente.updated_at = utcnow()
            uow.ingredientes.add(ingrediente)
