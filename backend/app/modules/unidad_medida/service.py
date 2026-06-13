from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.base_service import BaseService
from app.core.unit_of_work import UnitOfWork
from app.core.utils import utcnow
from app.modules.unidad_medida.models import UnidadMedida
from app.modules.unidad_medida.repository import UnidadMedidaRepository
from app.modules.unidad_medida.schemas import (
    UnidadMedidaCreate,
    UnidadMedidaList,
    UnidadMedidaPublic,
    UnidadMedidaUpdate,
)


class UnidadMedidaService(BaseService):
    def _repo(self) -> UnidadMedidaRepository:
        return UnidadMedidaRepository(self._session)

    def _get_or_404(self, repo: UnidadMedidaRepository, unidad_id: int) -> UnidadMedida:
        unidad = repo.get_active_by_id(unidad_id)
        if unidad is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unidad de medida con id={unidad_id} no encontrada",
            )
        return unidad

    def _normalize_codigo(self, codigo: str) -> str:
        return codigo.strip()

    def _to_public(self, unidad: UnidadMedida) -> UnidadMedidaPublic:
        return UnidadMedidaPublic(
            id=unidad.id or 0,
            codigo=unidad.codigo,
            nombre=unidad.nombre,
            simbolo=unidad.simbolo,
            descripcion=unidad.descripcion,
            created_at=unidad.created_at,
            updated_at=unidad.updated_at,
            deleted_at=unidad.deleted_at,
        )

    def list(self, page: int = 1, size: int = 100) -> UnidadMedidaList:
        repo = self._repo()
        offset = (page - 1) * size
        total = repo.count_active()
        return UnidadMedidaList(
            items=[self._to_public(unidad) for unidad in repo.list_active(offset, size)],
            total=total,
            page=page,
            size=size,
            pages=max(1, (total + size - 1) // size),
        )

    def get_by_id(self, unidad_id: int) -> UnidadMedidaPublic:
        repo = self._repo()
        return self._to_public(self._get_or_404(repo, unidad_id))

    def create(self, data: UnidadMedidaCreate) -> UnidadMedidaPublic:
        repo = self._repo()
        codigo = self._normalize_codigo(data.codigo)
        if repo.get_active_by_codigo(codigo) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una unidad de medida con ese codigo",
            )

        try:
            with UnitOfWork(self._session):
                unidad = UnidadMedida(
                    codigo=codigo,
                    nombre=data.nombre.strip(),
                    simbolo=data.simbolo.strip(),
                    descripcion=data.descripcion,
                )
                repo.add(unidad)
                result = self._to_public(unidad)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una unidad de medida con ese codigo",
            ) from exc

        return result

    def update(self, unidad_id: int, data: UnidadMedidaUpdate) -> UnidadMedidaPublic:
        repo = self._repo()
        with UnitOfWork(self._session):
            unidad = self._get_or_404(repo, unidad_id)
            patch = data.model_dump(exclude_unset=True)
            if "codigo" in patch:
                codigo = self._normalize_codigo(patch["codigo"])
                existing = repo.get_active_by_codigo(codigo)
                if existing is not None and existing.id != unidad_id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Ya existe una unidad de medida con ese codigo",
                    )
                patch["codigo"] = codigo

            for field, value in patch.items():
                setattr(unidad, field, value.strip() if isinstance(value, str) else value)

            unidad.updated_at = utcnow()
            repo.add(unidad)
            result = self._to_public(unidad)

        return result

    def soft_delete(self, unidad_id: int) -> None:
        repo = self._repo()
        with UnitOfWork(self._session):
            unidad = self._get_or_404(repo, unidad_id)
            unidad.deleted_at = utcnow()
            unidad.updated_at = utcnow()
            repo.add(unidad)
