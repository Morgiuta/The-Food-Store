from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.api.deps import DbSession
from app.modules.auth.dependencies import require_roles
from app.modules.auth.models import Usuario
from app.modules.direcciones.schemas import (
    DireccionCreate,
    DireccionPublic,
    DireccionUpdate,
)
from app.modules.direcciones.service import DireccionesService

router = APIRouter()


def get_direcciones_service(session: DbSession) -> DireccionesService:
    return DireccionesService(session)


@router.get("/", response_model=list[DireccionPublic])
def list_direcciones(
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    svc: DireccionesService = Depends(get_direcciones_service),
) -> list[DireccionPublic]:
    return svc.list_by_usuario(current_user.id or 0)


@router.post("/", response_model=DireccionPublic, status_code=status.HTTP_201_CREATED)
def create_direccion(
    data: DireccionCreate,
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    svc: DireccionesService = Depends(get_direcciones_service),
) -> DireccionPublic:
    return svc.create(current_user.id or 0, data)


@router.put("/{direccion_id}", response_model=DireccionPublic)
def update_direccion(
    direccion_id: Annotated[int, Path(gt=0)],
    data: DireccionUpdate,
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    svc: DireccionesService = Depends(get_direcciones_service),
) -> DireccionPublic:
    return svc.update(current_user.id or 0, direccion_id, data)


@router.patch("/{direccion_id}/principal", response_model=DireccionPublic)
def mark_direccion_principal(
    direccion_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    svc: DireccionesService = Depends(get_direcciones_service),
) -> DireccionPublic:
    return svc.mark_principal(current_user.id or 0, direccion_id)


@router.delete("/{direccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_direccion(
    direccion_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[
        Usuario,
        Depends(require_roles("ADMIN", "STOCK", "PEDIDOS", "CLIENT")),
    ],
    svc: DireccionesService = Depends(get_direcciones_service),
) -> None:
    svc.soft_delete(current_user.id or 0, direccion_id)
