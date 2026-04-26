from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import DbSession
from app.modules.categoria.schemas import (
    CategoriaCreate,
    CategoriaList,
    CategoriaPublic,
    CategoriaUpdate,
)
from app.modules.categoria.service import CategoriaService

router = APIRouter()


def get_categoria_service(session: DbSession) -> CategoriaService:
    return CategoriaService(session)


@router.post("/", response_model=CategoriaPublic, status_code=status.HTTP_201_CREATED)
def create_categoria(
    data: CategoriaCreate,
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaPublic:
    return svc.create(data)


@router.get("/", response_model=CategoriaList)
def list_categorias(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaList:
    return svc.get_all(offset=offset, limit=limit)


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
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaPublic:
    return svc.update(categoria_id, data)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(
    categoria_id: Annotated[int, Path(gt=0)],
    svc: CategoriaService = Depends(get_categoria_service),
) -> None:
    svc.soft_delete(categoria_id)
