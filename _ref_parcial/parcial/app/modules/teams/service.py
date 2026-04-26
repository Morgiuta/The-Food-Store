# app/modules/teams/service.py
from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.teams.models import Team
from app.modules.teams.schemas import (
    TeamCreate, TeamPublic, TeamUpdate, TeamList, TeamWithHeroes,
)
from app.modules.teams.unit_of_work import TeamUnitOfWork
from app.modules.heroes.schemas import HeroPublic


class TeamService:
    """
    Servicio de aplicación para la entidad Team.

    Responsabilidad:
    - Orquestar casos de uso relacionados a equipos
    - Coordinar múltiples repositorios mediante UnitOfWork
    - Validar reglas de negocio a nivel aplicación

    Características:
    - Soporta operaciones cross-module (Team + Hero)
    - Mantiene consistencia transaccional usando TeamUnitOfWork
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa el servicio con una sesión de base de datos.

        Args:
            session (Session): Sesión activa utilizada por el UnitOfWork.
        """
        self._session = session

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_or_404(self, uow: TeamUnitOfWork, team_id: int) -> Team:
        """
        Obtiene un Team por ID o lanza HTTP 404 si no existe.

        Args:
            uow (TeamUnitOfWork): Unidad de trabajo activa.
            team_id (int): ID del equipo.

        Returns:
            Team: Instancia encontrada.

        Raises:
            HTTPException: 404 si no existe.
        """
        team = uow.teams.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team con id={team_id} no encontrado",
            )
        return team

    def _assert_name_unique(self, uow: TeamUnitOfWork, name: str) -> None:
        """
        Valida que el nombre del equipo sea único.

        Args:
            uow (TeamUnitOfWork): Unidad de trabajo activa.
            name (str): Nombre a validar.

        Raises:
            HTTPException: 409 si el nombre ya existe.

        Nota:
            No reemplaza un constraint UNIQUE en la base de datos.
        """
        if uow.teams.get_by_name(name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un equipo con el nombre '{name}'",
            )

    # ── Casos de uso ──────────────────────────────────────────────────────────

    def create(self, data: TeamCreate) -> TeamPublic:
        """
        Crea un nuevo equipo.

        Flujo:
        - Valida unicidad del nombre
        - Construye entidad
        - Persiste en DB
        - Serializa resultado

        Args:
            data (TeamCreate): Datos de entrada.

        Returns:
            TeamPublic: DTO del equipo creado.
        """
        with TeamUnitOfWork(self._session) as uow:
            self._assert_name_unique(uow, data.name)
            team = Team.model_validate(data)
            uow.teams.add(team)
            result = TeamPublic.model_validate(team)
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> TeamList:
        """
        Obtiene equipos activos con paginación.

        Args:
            offset (int): Offset de paginación.
            limit (int): Límite de resultados.

        Returns:
            TeamList: DTO con lista y total.
        """
        with TeamUnitOfWork(self._session) as uow:
            teams = uow.teams.get_active(offset=offset, limit=limit)
            total = uow.teams.count()

            result = TeamList(
                data=[TeamPublic.model_validate(t) for t in teams],
                total=total,
            )
        return result

    def get_by_id(self, team_id: int) -> TeamPublic:
        """
        Obtiene un equipo por ID.

        Args:
            team_id (int): ID del equipo.

        Returns:
            TeamPublic: DTO del equipo.
        """
        with TeamUnitOfWork(self._session) as uow:
            team = self._get_or_404(uow, team_id)
            result = TeamPublic.model_validate(team)
        return result

    def get_with_heroes(self, team_id: int) -> TeamWithHeroes:
        """
        Obtiene un equipo junto con sus héroes asociados.

        Caso cross-module:
        - Consulta Team
        - Consulta Heroes relacionados

        Args:
            team_id (int): ID del equipo.

        Returns:
            TeamWithHeroes: DTO con datos embebidos.
        """
        with TeamUnitOfWork(self._session) as uow:
            team = self._get_or_404(uow, team_id)
            heroes = uow.heroes.get_by_team(team_id)

            team_data = team.model_dump()
            heroes_data = [HeroPublic.model_validate(h) for h in heroes]

        return TeamWithHeroes.model_validate({
            **team_data,
            "heroes": heroes_data,
        })

    def update(self, team_id: int, data: TeamUpdate) -> TeamPublic:
        """
        Actualiza un equipo de forma parcial.

        Args:
            team_id (int): ID del equipo.
            data (TeamUpdate): Datos a actualizar.

        Returns:
            TeamPublic: DTO actualizado.
        """
        with TeamUnitOfWork(self._session) as uow:
            team = self._get_or_404(uow, team_id)

            if data.name and data.name != team.name:
                self._assert_name_unique(uow, data.name)

            patch = data.model_dump(exclude_unset=True)

            for field, value in patch.items():
                setattr(team, field, value)

            uow.teams.add(team)
            result = TeamPublic.model_validate(team)

        return result

    def assign_hero(self, team_id: int, hero_id: int) -> TeamWithHeroes:
        """
        Asigna un héroe a un equipo dentro de una misma transacción.

        Flujo:
        - Valida existencia de Team
        - Valida existencia y estado de Hero
        - Asigna relación
        - Persiste cambios
        - Devuelve estado actualizado

        Args:
            team_id (int): ID del equipo.
            hero_id (int): ID del héroe.

        Returns:
            TeamWithHeroes: DTO actualizado.
        """
        with TeamUnitOfWork(self._session) as uow:
            team = self._get_or_404(uow, team_id)

            hero = uow.heroes.get_by_id(hero_id)
            if not hero:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Hero con id={hero_id} no encontrado",
                )

            if not hero.is_active:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="No se puede asignar un héroe inactivo a un equipo",
                )

            hero.team_id = team.id
            uow.heroes.add(hero)

            team_data = team.model_dump()
            all_heroes = uow.heroes.get_by_team(team_id)
            heroes_data = [HeroPublic.model_validate(h) for h in all_heroes]

        return TeamWithHeroes.model_validate({
            **team_data,
            "heroes": heroes_data,
        })

    def soft_delete(self, team_id: int) -> None:
        """
        Realiza un borrado lógico del equipo.

        Args:
            team_id (int): ID del equipo.
        """
        with TeamUnitOfWork(self._session) as uow:
            team = self._get_or_404(uow, team_id)
            team.is_active = False
            uow.teams.add(team)