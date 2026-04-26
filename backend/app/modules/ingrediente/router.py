from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import DbSession
from app.modules.ingrediente.schemas import (
    IngredienteCreate,
    IngredienteList,
    IngredientePublic,
    IngredienteUpdate,
)
from app.modules.ingrediente.service import IngredienteService

router = APIRouter()


def get_ingrediente_service(session: DbSession) -> IngredienteService:
    return IngredienteService(session)


@router.post("/", response_model=IngredientePublic, status_code=status.HTTP_201_CREATED)
def create_ingrediente(
    data: IngredienteCreate,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredientePublic:
    return svc.create(data)


@router.get("/", response_model=IngredienteList)
def list_ingredientes(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredienteList:
    return svc.get_all(offset=offset, limit=limit)


@router.get("/{ingrediente_id}", response_model=IngredientePublic)
def get_ingrediente(
    ingrediente_id: Annotated[int, Path(gt=0)],
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredientePublic:
    return svc.get_by_id(ingrediente_id)


@router.patch("/{ingrediente_id}", response_model=IngredientePublic)
def update_ingrediente(
    ingrediente_id: Annotated[int, Path(gt=0)],
    data: IngredienteUpdate,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredientePublic:
    return svc.update(ingrediente_id, data)


@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingrediente(
    ingrediente_id: Annotated[int, Path(gt=0)],
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> None:
    svc.delete(ingrediente_id)
