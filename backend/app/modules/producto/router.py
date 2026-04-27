from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import DbSession
from app.modules.producto.schemas import (
    ProductoCreate,
    ProductoList,
    ProductoPublic,
    ProductoUpdate,
)
from app.modules.producto.service import ProductoService

router = APIRouter()


def get_producto_service(session: DbSession) -> ProductoService:
    return ProductoService(session)


@router.post("/", response_model=ProductoPublic, status_code=status.HTTP_201_CREATED)
def create_producto(
    data: ProductoCreate,
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoPublic:
    return svc.create(data)


@router.get("/", response_model=ProductoList)
def list_productos(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoList:
    return svc.get_all(offset=offset, limit=limit)


@router.get("/{producto_id}", response_model=ProductoPublic)
def get_producto(
    producto_id: Annotated[int, Path(gt=0)],
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoPublic:
    return svc.get_by_id(producto_id)


@router.patch("/{producto_id}", response_model=ProductoPublic)
def update_producto(
    producto_id: Annotated[int, Path(gt=0)],
    data: ProductoUpdate,
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoPublic:
    return svc.update(producto_id, data)


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(
    producto_id: Annotated[int, Path(gt=0)],
    svc: ProductoService = Depends(get_producto_service),
) -> None:
    svc.soft_delete(producto_id)
