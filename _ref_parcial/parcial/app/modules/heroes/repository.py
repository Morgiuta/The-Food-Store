# app/modules/heroes/repository.py
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.heroes.models import Hero


class HeroRepository(BaseRepository[Hero]):
    """
    Repositorio de Heroes.
    Agrega queries específicas del dominio sobre el CRUD base.
    Solo habla con la DB — nunca levanta HTTPException.
    """
    def __init__(self, session: Session) -> None:
            """
            Inicializa el repositorio de Hero.

            Args:
                session (Session): Sesión activa de base de datos.
            """
            super().__init__(session, Hero)

    def get_by_alias(self, alias: str) -> Hero | None:
        """
        Obtiene un héroe por su alias.

        Args:
            alias (str): Alias del héroe.

        Returns:
            Hero | None: Instancia encontrada o None si no existe.

        Nota:
            Se asume que 'alias' es único a nivel de base de datos.
        """
        return self.session.exec(
            select(Hero).where(Hero.alias == alias)
        ).first()

    def get_active(self, offset: int = 0, limit: int = 20) -> list[Hero]:
        """
        Obtiene héroes activos con paginación.

        Args:
            offset (int): Cantidad de registros a omitir.
            limit (int): Máximo de registros a devolver.

        Returns:
            list[Hero]: Lista de héroes activos.

        Nota:
            - No se define orden explícito → resultados no determinísticos
            - Se usa '== True' por limitaciones del ORM (evita warnings de estilo)
        """
        return list(
            self.session.exec(
                select(Hero)
                .where(Hero.is_active == True)  # noqa: E712
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def get_by_team(self, team_id: int) -> list[Hero]:
        """
        Obtiene todos los héroes asociados a un equipo.

        Args:
            team_id (int): ID del equipo.

        Returns:
            list[Hero]: Lista de héroes pertenecientes al equipo.
        """
        return list(
            self.session.exec(
                select(Hero).where(Hero.team_id == team_id)
            ).all()
        )

    def count(self) -> int:
        """
        Cuenta la cantidad total de héroes.

        Returns:
            int: Total de registros en la tabla Hero.
        """
        return len(self.session.exec(select(Hero)).all())
