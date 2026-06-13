from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import DbSession
from app.modules.auth.dependencies import require_roles
from app.modules.unidad_medida.schemas import (
    UnidadMedidaCreate,
    UnidadMedidaList,
    UnidadMedidaPublic,
    UnidadMedidaUpdate,
)
from app.modules.unidad_medida.service import UnidadMedidaService

router = APIRouter()


def get_unidad_medida_service(session: DbSession) -> UnidadMedidaService:
    return UnidadMedidaService(session)


@router.get("/", response_model=UnidadMedidaList)
def list_unidades_medida(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 100,
    svc: UnidadMedidaService = Depends(get_unidad_medida_service),
) -> UnidadMedidaList:
    return svc.list(page=page, size=size)


@router.get("/{unidad_id}", response_model=UnidadMedidaPublic)
def get_unidad_medida(
    unidad_id: Annotated[int, Path(gt=0)],
    svc: UnidadMedidaService = Depends(get_unidad_medida_service),
) -> UnidadMedidaPublic:
    return svc.get_by_id(unidad_id)


@router.post(
    "/",
    response_model=UnidadMedidaPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_unidad_medida(
    data: UnidadMedidaCreate,
    _current_user=Depends(require_roles("ADMIN")),
    svc: UnidadMedidaService = Depends(get_unidad_medida_service),
) -> UnidadMedidaPublic:
    return svc.create(data)


@router.patch("/{unidad_id}", response_model=UnidadMedidaPublic)
def update_unidad_medida(
    unidad_id: Annotated[int, Path(gt=0)],
    data: UnidadMedidaUpdate,
    _current_user=Depends(require_roles("ADMIN")),
    svc: UnidadMedidaService = Depends(get_unidad_medida_service),
) -> UnidadMedidaPublic:
    return svc.update(unidad_id, data)


@router.delete("/{unidad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unidad_medida(
    unidad_id: Annotated[int, Path(gt=0)],
    _current_user=Depends(require_roles("ADMIN")),
    svc: UnidadMedidaService = Depends(get_unidad_medida_service),
) -> None:
    svc.soft_delete(unidad_id)
