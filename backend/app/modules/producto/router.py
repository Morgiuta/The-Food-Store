from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import DbSession
from app.modules.auth.dependencies import require_permission
from app.modules.producto.schemas import (
    ProductoCreate,
    ProductoDisponibilidadUpdate,
    ProductoList,
    ProductoPublic,
    ProductoStockUpdate,
    ProductoUpdate,
)
from app.modules.producto.service import ProductoService

router = APIRouter()


def get_producto_service(session: DbSession) -> ProductoService:
    return ProductoService(session)


@router.post("/", response_model=ProductoPublic, status_code=status.HTTP_201_CREATED)
def create_producto(
    data: ProductoCreate,
    _current_user=Depends(require_permission("producto", "manage")),
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoPublic:
    return svc.create(data)


@router.get("/", response_model=ProductoList)
def list_productos(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
    categoria_id: Annotated[int | None, Query(gt=0)] = None,
    disponible: Annotated[bool | None, Query()] = None,
    q: Annotated[str | None, Query(max_length=150)] = None,
    include_deleted: Annotated[bool, Query()] = False,
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoList:
    return svc.get_all(
        page=page,
        size=size,
        categoria_id=categoria_id,
        disponible=disponible,
        q=q,
        include_deleted=include_deleted,
    )


@router.get("/{producto_id}", response_model=ProductoPublic)
def get_producto(
    producto_id: Annotated[int, Path(gt=0)],
    _current_user=Depends(require_permission("producto", "read")),
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoPublic:
    return svc.get_by_id(producto_id)


@router.patch("/{producto_id}", response_model=ProductoPublic)
def update_producto(
    producto_id: Annotated[int, Path(gt=0)],
    data: ProductoUpdate,
    _current_user=Depends(require_permission("producto", "manage")),
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoPublic:
    return svc.update(producto_id, data)


@router.patch("/{producto_id}/disponibilidad", response_model=ProductoPublic)
def update_producto_disponibilidad(
    producto_id: Annotated[int, Path(gt=0)],
    data: ProductoDisponibilidadUpdate,
    _current_user=Depends(require_permission("producto", "disponibilidad")),
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoPublic:
    return svc.update_disponibilidad(producto_id, data)


from app.modules.producto.schemas import ImagenProductoUpdate
@router.patch("/{producto_id}/imagenes", response_model=ProductoPublic)
def update_producto_imagenes(
    producto_id: Annotated[int, Path(gt=0)],
    data: ImagenProductoUpdate,
    _current_user=Depends(require_permission("producto", "manage")),
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoPublic:
    return svc.update_imagenes(producto_id, data)


@router.patch("/{producto_id}/stock", response_model=ProductoPublic)
def update_producto_stock(
    producto_id: Annotated[int, Path(gt=0)],
    data: ProductoStockUpdate,
    _current_user=Depends(require_permission("producto", "stock")),
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoPublic:
    return svc.update_stock(producto_id, data)


@router.patch("/{producto_id}/stock/cantidad", response_model=ProductoPublic)
def update_producto_stock_cantidad(
    producto_id: Annotated[int, Path(gt=0)],
    data: ProductoStockUpdate,
    _current_user=Depends(require_permission("producto", "stock")),
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoPublic:
    return svc.update_stock(producto_id, data)


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(
    producto_id: Annotated[int, Path(gt=0)],
    _current_user=Depends(require_permission("producto", "manage")),
    svc: ProductoService = Depends(get_producto_service),
) -> None:
    svc.soft_delete(producto_id)


@router.patch("/{producto_id}/restore", response_model=ProductoPublic)
def restore_producto(
    producto_id: Annotated[int, Path(gt=0)],
    _current_user=Depends(require_permission("producto", "manage")),
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoPublic:
    return svc.restore(producto_id)
