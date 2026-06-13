from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status

from app.api.deps import DbSession
from app.modules.auth.dependencies import require_roles
from app.modules.categoria.schemas import (
    CategoriaCreate,
    CategoriaList,
    CategoriaPublic,
    CategoriaTree,
    CategoriaUpdate,
)
from app.modules.categoria.service import CategoriaService

router = APIRouter()


def get_categoria_service(session: DbSession) -> CategoriaService:
    return CategoriaService(session)


@router.post("/", response_model=CategoriaPublic, status_code=status.HTTP_201_CREATED)
def create_categoria(
    data: CategoriaCreate,
    _current_user=Depends(require_roles("ADMIN")),
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaPublic:
    return svc.create(data)


@router.get("/", response_model=CategoriaList)
def list_categorias(
    request: Request,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
    parent_id: Annotated[str | None, Query()] = None,
    include_deleted: Annotated[bool, Query()] = False,
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaList:
    filter_parent = "parent_id" in request.query_params
    parent_id_value: int | None = None

    if filter_parent and (
        parent_id is not None and parent_id.strip().lower() not in ("", "null")
    ):
        try:
            parent_id_value = int(parent_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="parent_id debe ser un entero o null",
            ) from exc

        if parent_id_value <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="parent_id debe ser mayor a 0",
            )

    return svc.get_all(
        page=page,
        size=size,
        parent_id=parent_id_value,
        filter_parent=filter_parent,
        include_deleted=include_deleted,
    )


@router.get("/tree", response_model=list[CategoriaTree])
def get_categorias_tree(
    include_deleted: Annotated[bool, Query()] = False,
    svc: CategoriaService = Depends(get_categoria_service),
) -> list[CategoriaTree]:
    return svc.get_tree(include_deleted=include_deleted)


@router.get("/{categoria_id}", response_model=CategoriaPublic)
def get_categoria(
    categoria_id: Annotated[int, Path(gt=0)],
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaPublic:
    return svc.get_by_id(categoria_id)


@router.patch("/{categoria_id}", response_model=CategoriaPublic)
def update_categoria(
    categoria_id: Annotated[int, Path(gt=0)],
    data: CategoriaUpdate,
    _current_user=Depends(require_roles("ADMIN")),
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaPublic:
    return svc.update(categoria_id, data)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(
    categoria_id: Annotated[int, Path(gt=0)],
    _current_user=Depends(require_roles("ADMIN")),
    svc: CategoriaService = Depends(get_categoria_service),
) -> None:
    svc.soft_delete(categoria_id)


@router.patch("/{categoria_id}/restore", response_model=CategoriaPublic)
def restore_categoria(
    categoria_id: Annotated[int, Path(gt=0)],
    _current_user=Depends(require_roles("ADMIN")),
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaPublic:
    return svc.restore(categoria_id)
