from fastapi import HTTPException, status

from app.core.base_service import BaseService
from app.core.utils import utcnow
from app.modules.ingrediente.models import Ingrediente
from app.modules.ingrediente.schemas import (
    IngredienteCreate,
    IngredienteList,
    IngredientePublic,
    IngredienteUpdate,
)
from app.modules.ingrediente.unit_of_work import IngredienteUnitOfWork


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
        ingrediente = uow.ingredientes.get_by_nombre(nombre)
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

    def get_all(self, offset: int = 0, limit: int = 20) -> IngredienteList:
        with IngredienteUnitOfWork(self._session) as uow:
            ingredientes = uow.ingredientes.list_all(offset=offset, limit=limit)
            total = uow.ingredientes.count_all()
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
            patch = data.model_dump(exclude_unset=True)

            if "nombre" in patch:
                self._assert_nombre_unique(uow, patch["nombre"], current_id=ingrediente.id)

            for field, value in patch.items():
                setattr(ingrediente, field, value)

            ingrediente.updated_at = utcnow()
            uow.ingredientes.add(ingrediente)
            result = IngredientePublic.model_validate(ingrediente)
        return result

    def delete(self, ingrediente_id: int) -> None:
        with IngredienteUnitOfWork(self._session) as uow:
            ingrediente = self._get_or_404(uow, ingrediente_id)
            uow.ingredientes.session.delete(ingrediente)
            uow.ingredientes.session.flush()
