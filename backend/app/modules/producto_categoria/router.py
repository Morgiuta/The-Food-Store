from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import DbSession
from app.modules.producto_categoria.schemas import (
    ProductoCategoriaCreate,
    ProductoCategoriaList,
    ProductoCategoriaPublic,
    ProductoCategoriaUpdate,
)
from app.modules.producto_categoria.service import ProductoCategoriaService

router = APIRouter()


def get_producto_categoria_service(session: DbSession) -> ProductoCategoriaService:
    return ProductoCategoriaService(session)


@router.post("/", response_model=ProductoCategoriaPublic, status_code=status.HTTP_201_CREATED)
def create_producto_categoria(
    data: ProductoCategoriaCreate,
    svc: ProductoCategoriaService = Depends(get_producto_categoria_service),
) -> ProductoCategoriaPublic:
    return svc.create(data)


@router.get("/", response_model=ProductoCategoriaList)
def list_producto_categorias(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    svc: ProductoCategoriaService = Depends(get_producto_categoria_service),
) -> ProductoCategoriaList:
    return svc.get_all(offset=offset, limit=limit)


@router.get("/{producto_id}/{categoria_id}", response_model=ProductoCategoriaPublic)
def get_producto_categoria(
    producto_id: Annotated[int, Path(gt=0)],
    categoria_id: Annotated[int, Path(gt=0)],
    svc: ProductoCategoriaService = Depends(get_producto_categoria_service),
) -> ProductoCategoriaPublic:
    return svc.get_by_id(producto_id, categoria_id)


@router.patch("/{producto_id}/{categoria_id}", response_model=ProductoCategoriaPublic)
def update_producto_categoria(
    producto_id: Annotated[int, Path(gt=0)],
    categoria_id: Annotated[int, Path(gt=0)],
    data: ProductoCategoriaUpdate,
    svc: ProductoCategoriaService = Depends(get_producto_categoria_service),
) -> ProductoCategoriaPublic:
    return svc.update(producto_id, categoria_id, data)


@router.delete("/{producto_id}/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto_categoria(
    producto_id: Annotated[int, Path(gt=0)],
    categoria_id: Annotated[int, Path(gt=0)],
    svc: ProductoCategoriaService = Depends(get_producto_categoria_service),
) -> None:
    svc.delete(producto_id, categoria_id)
