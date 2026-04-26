# app/modules/heroes/service.py
from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.heroes.models import Hero
from app.modules.heroes.schemas import HeroCreate, HeroPublic, HeroUpdate, HeroList
from app.modules.heroes.unit_of_work import HeroUnitOfWork


class HeroService:
    """
    Capa de lógica de negocio para Heroes.

    Responsabilidades:
    - Validaciones de dominio (alias único, etc.)
    - Coordinar repositorios a través del UoW
    - Levantar HTTPException cuando corresponde
    - NUNCA acceder directamente a la Session

    REGLA IMPORTANTE — objetos ORM y commit():
    Después de que el UoW hace commit(), SQLAlchemy expira los atributos
    del objeto ORM. Toda serialización (model_dump / model_validate)
    debe ocurrir DENTRO del bloque `with uow:`, antes de que __exit__
    dispare el commit.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa el servicio con una sesión de base de datos.

        Args:
            session (Session): Sesión activa que será utilizada por el UnitOfWork.

        Nota:
            El servicio no maneja directamente la transacción; delega en HeroUnitOfWork.
        """
        self._session = session


    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_or_404(self, uow: HeroUnitOfWork, hero_id: int) -> Hero:
        """
        Obtiene un héroe por ID o lanza excepción HTTP 404 si no existe.

        Args:
            uow (HeroUnitOfWork): Unidad de trabajo activa.
            hero_id (int): ID del héroe.

        Returns:
            Hero: Instancia encontrada.

        Raises:
            HTTPException: 404 si el héroe no existe.

        """
        hero = uow.heroes.get_by_id(hero_id)
        if not hero:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hero con id={hero_id} no encontrado",
            )
        return hero


    def _assert_alias_unique(self, uow: HeroUnitOfWork, alias: str) -> None:
        """
        Valida que el alias no esté en uso.

        Args:
            uow (HeroUnitOfWork): Unidad de trabajo activa.
            alias (str): Alias a validar.

        Raises:
            HTTPException: 409 si el alias ya existe.

        Nota:
            Esta validación es a nivel aplicación, no reemplaza un UNIQUE en DB.
        """
        if uow.heroes.get_by_alias(alias):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El alias '{alias}' ya está en uso",
            )

    def _get_team_or_404(self, uow: HeroUnitOfWork, team_id: int):
        team = uow.teams.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=404,
                detail=f"Team con id={team_id} no encontrado"
            )
        return team

    # ── Casos de uso ─────────────────────────────────────────────────────────

    def create(self, data: HeroCreate) -> HeroPublic:
        """
        Crea un nuevo héroe.

        Flujo:
        - Valida unicidad de alias
        - Construye entidad desde DTO
        - Persiste usando repositorio
        - Serializa antes de cerrar la transacción

        Args:
            data (HeroCreate): Datos de entrada.

        Returns:
            HeroPublic: DTO de salida.
        """
        with HeroUnitOfWork(self._session) as uow:
            self._assert_alias_unique(uow, data.alias)
            self._get_team_or_404(uow, data.team_id)
            hero = Hero.model_validate(data)
            uow.heroes.add(hero)

            # Serializar dentro del contexto asegura acceso a atributos lazy
            result = HeroPublic.model_validate(hero)

        return result


    def get_all(self, offset: int = 0, limit: int = 20) -> HeroList:
        """
        Obtiene lista paginada de héroes activos.

        Args:
            offset (int): Desplazamiento.
            limit (int): Límite de resultados.

        Returns:
            HeroList: DTO con lista de héroes y total.

        Nota:
            El total se calcula con una query separada.
        """
        with HeroUnitOfWork(self._session) as uow:
            heroes = uow.heroes.get_active(offset=offset, limit=limit)
            total = uow.heroes.count()

            result = HeroList(
                data=[HeroPublic.model_validate(h) for h in heroes],
                total=total,
            )

        return result


    def get_by_id(self, hero_id: int) -> HeroPublic:
        """
        Obtiene un héroe por ID.

        Args:
            hero_id (int): ID del héroe.

        Returns:
            HeroPublic: DTO del héroe.

        Raises:
            HTTPException: 404 si no existe.
        """
        with HeroUnitOfWork(self._session) as uow:
            hero = self._get_or_404(uow, hero_id)
            result = HeroPublic.model_validate(hero)

        return result


    def update(self, hero_id: int, data: HeroUpdate) -> HeroPublic:
        """
        Actualiza un héroe existente de forma parcial (PATCH).

        Flujo:
        - Obtiene entidad
        - Valida alias si cambia
        - Aplica cambios dinámicamente
        - Persiste cambios

        Args:
            hero_id (int): ID del héroe.
            data (HeroUpdate): Datos parciales.

        Returns:
            HeroPublic: DTO actualizado.
        """
        with HeroUnitOfWork(self._session) as uow:
            hero = self._get_or_404(uow, hero_id)

            if data.alias and data.alias != hero.alias:
                self._assert_alias_unique(uow, data.alias)

            if data.team_id and data.team_id != hero.team_id:
                self._get_team_or_404(uow, data.team_id)

            # Solo campos enviados por el cliente
            patch = data.model_dump(exclude_unset=True)

            for field, value in patch.items():
                setattr(hero, field, value)

            uow.heroes.add(hero)
            result = HeroPublic.model_validate(hero)

        return result


    def soft_delete(self, hero_id: int) -> None:
        """
        Realiza un borrado lógico del héroe.

        Flujo:
        - Obtiene entidad
        - Marca como inactivo
        - Persiste cambio

        Args:
            hero_id (int): ID del héroe.

        Nota:
            No elimina físicamente el registro de la base de datos.
        """
        with HeroUnitOfWork(self._session) as uow:
            hero = self._get_or_404(uow, hero_id)
            hero.is_active = False
            uow.heroes.add(hero)