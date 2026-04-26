from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import DbSession
from app.modules.producto_ingrediente.schemas import (
    ProductoIngredienteCreate,
    ProductoIngredienteList,
    ProductoIngredientePublic,
    ProductoIngredienteUpdate,
)
from app.modules.producto_ingrediente.service import ProductoIngredienteService

router = APIRouter()


def get_producto_ingrediente_service(session: DbSession) -> ProductoIngredienteService:
    return ProductoIngredienteService(session)


@router.post("/", response_model=ProductoIngredientePublic, status_code=status.HTTP_201_CREATED)
def create_producto_ingrediente(
    data: ProductoIngredienteCreate,
    svc: ProductoIngredienteService = Depends(get_producto_ingrediente_service),
) -> ProductoIngredientePublic:
    return svc.create(data)


@router.get("/", response_model=ProductoIngredienteList)
def list_producto_ingredientes(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    svc: ProductoIngredienteService = Depends(get_producto_ingrediente_service),
) -> ProductoIngredienteList:
    return svc.get_all(offset=offset, limit=limit)


@router.get("/{producto_id}/{ingrediente_id}", response_model=ProductoIngredientePublic)
def get_producto_ingrediente(
    producto_id: Annotated[int, Path(gt=0)],
    ingrediente_id: Annotated[int, Path(gt=0)],
    svc: ProductoIngredienteService = Depends(get_producto_ingrediente_service),
) -> ProductoIngredientePublic:
    return svc.get_by_id(producto_id, ingrediente_id)


@router.patch("/{producto_id}/{ingrediente_id}", response_model=ProductoIngredientePublic)
def update_producto_ingrediente(
    producto_id: Annotated[int, Path(gt=0)],
    ingrediente_id: Annotated[int, Path(gt=0)],
    data: ProductoIngredienteUpdate,
    svc: ProductoIngredienteService = Depends(get_producto_ingrediente_service),
) -> ProductoIngredientePublic:
    return svc.update(producto_id, ingrediente_id, data)


@router.delete("/{producto_id}/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto_ingrediente(
    producto_id: Annotated[int, Path(gt=0)],
    ingrediente_id: Annotated[int, Path(gt=0)],
    svc: ProductoIngredienteService = Depends(get_producto_ingrediente_service),
) -> None:
    svc.delete(producto_id, ingrediente_id)
