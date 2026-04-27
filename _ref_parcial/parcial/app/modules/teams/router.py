# app/modules/teams/router.py
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.teams.schemas import (
    TeamCreate, TeamPublic, TeamUpdate, TeamList, TeamWithHeroes,
)
from app.modules.teams.service import TeamService

router = APIRouter()


def get_team_service(session: Session = Depends(get_session)) -> TeamService:
    return TeamService(session)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=TeamPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un equipo",
)
def create_team(
    data: TeamCreate,
    svc: TeamService = Depends(get_team_service),
) -> TeamPublic:
    return svc.create(data)


@router.get(
    "/",
    response_model=TeamList,
    summary="Listar equipos activos (paginado)",
)
def list_teams(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: TeamService = Depends(get_team_service),
) -> TeamList:
    return svc.get_all(offset=offset, limit=limit)


@router.get(
    "/{team_id}",
    response_model=TeamPublic,
    summary="Obtener equipo por ID",
)
def get_team(
    team_id: int,
    svc: TeamService = Depends(get_team_service),
) -> TeamPublic:
    return svc.get_by_id(team_id)


@router.get(
    "/{team_id}/heroes",
    response_model=TeamWithHeroes,
    summary="Obtener equipo con sus héroes",
)
def get_team_with_heroes(
    team_id: int,
    svc: TeamService = Depends(get_team_service),
) -> TeamWithHeroes:
    return svc.get_with_heroes(team_id)


@router.patch(
    "/{team_id}",
    response_model=TeamPublic,
    summary="Actualización parcial de equipo",
)
def update_team(
    team_id: int,
    data: TeamUpdate,
    svc: TeamService = Depends(get_team_service),
) -> TeamPublic:
    return svc.update(team_id, data)


@router.post(
    "/{team_id}/heroes/{hero_id}",
    response_model=TeamWithHeroes,
    status_code=status.HTTP_200_OK,
    summary="Asignar héroe a equipo (cross-module, una transacción)",
)
def assign_hero_to_team(
    team_id: int,
    hero_id: int,
    svc: TeamService = Depends(get_team_service),
) -> TeamWithHeroes:
    return svc.assign_hero(team_id, hero_id)


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete de equipo",
)
def delete_team(
    team_id: int,
    svc: TeamService = Depends(get_team_service),
) -> None:
    svc.soft_delete(team_id)
