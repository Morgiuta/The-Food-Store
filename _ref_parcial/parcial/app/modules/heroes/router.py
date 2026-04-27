# app/modules/heroes/router.py
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.heroes.schemas import HeroCreate, HeroPublic, HeroUpdate, HeroList
from app.modules.heroes.service import HeroService

router = APIRouter()


def get_hero_service(session: Session = Depends(get_session)) -> HeroService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return HeroService(session)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=HeroPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un héroe",
)
def create_hero(
    data: HeroCreate,
    svc: HeroService = Depends(get_hero_service),
) -> HeroPublic:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.create(data)


@router.get(
    "/",
    response_model=HeroList,
    summary="Listar héroes activos (paginado)",
)
def list_heroes(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: HeroService = Depends(get_hero_service),
) -> HeroList:
    return svc.get_all(offset=offset, limit=limit)


@router.get(
    "/{hero_id}",
    response_model=HeroPublic,
    summary="Obtener héroe por ID",
)
def get_hero(
    hero_id: int,
    svc: HeroService = Depends(get_hero_service),
) -> HeroPublic:
    return svc.get_by_id(hero_id)


@router.patch(
    "/{hero_id}",
    response_model=HeroPublic,
    summary="Actualización parcial de héroe",
)
def update_hero(
    hero_id: int,
    data: HeroUpdate,
    svc: HeroService = Depends(get_hero_service),
) -> HeroPublic:
    return svc.update(hero_id, data)


@router.delete(
    "/{hero_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete de héroe",
)
def delete_hero(
    hero_id: int,
    svc: HeroService = Depends(get_hero_service),
) -> None:
    svc.soft_delete(hero_id)
