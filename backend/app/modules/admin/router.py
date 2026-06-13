from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import DbSession
from app.modules.admin.schemas import (
    UsuarioList,
    UsuarioPublic,
    UsuarioRolUpdate,
    UsuarioUpdate,
)
from app.modules.admin.service import UsuarioService
from app.modules.auth.dependencies import require_roles

router = APIRouter(dependencies=[Depends(require_roles("ADMIN"))])


def get_usuario_service(session: DbSession) -> UsuarioService:
    return UsuarioService(session)


@router.get("/usuarios/", response_model=UsuarioList)
def list_usuarios(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
    rol: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    svc: UsuarioService = Depends(get_usuario_service),
) -> UsuarioList:
    return svc.list(page=page, size=size, rol=rol)


@router.get("/usuarios/{usuario_id}", response_model=UsuarioPublic)
def get_usuario(
    usuario_id: Annotated[int, Path(gt=0)],
    svc: UsuarioService = Depends(get_usuario_service),
) -> UsuarioPublic:
    return svc.get_by_id(usuario_id)


@router.patch("/usuarios/{usuario_id}", response_model=UsuarioPublic)
def update_usuario(
    usuario_id: Annotated[int, Path(gt=0)],
    data: UsuarioUpdate,
    svc: UsuarioService = Depends(get_usuario_service),
) -> UsuarioPublic:
    return svc.update(usuario_id, data)


@router.delete("/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario(
    usuario_id: Annotated[int, Path(gt=0)],
    svc: UsuarioService = Depends(get_usuario_service),
) -> None:
    svc.soft_delete(usuario_id)


@router.patch("/usuarios/{usuario_id}/rol", response_model=UsuarioPublic)
def assign_usuario_rol(
    usuario_id: Annotated[int, Path(gt=0)],
    data: UsuarioRolUpdate,
    svc: UsuarioService = Depends(get_usuario_service),
) -> UsuarioPublic:
    return svc.assign_rol(usuario_id, data)
