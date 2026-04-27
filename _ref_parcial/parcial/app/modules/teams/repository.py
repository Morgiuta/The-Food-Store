from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.teams.models import Team


class TeamRepository(BaseRepository[Team]):
    """
    Repositorio específico para la entidad Team.

    Extiende el CRUD base provisto por BaseRepository e incorpora
    consultas propias del dominio relacionadas a equipos.

    Responsabilidad:
    - Ejecutar queries sobre Team
    - Encapsular acceso a datos
    - Mantener separación de la lógica de negocio

    Restricciones:
    - No contiene lógica de negocio
    - No lanza excepciones HTTP
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa el repositorio de Team.

        Args:
            session (Session): Sesión activa de base de datos.
        """
        super().__init__(session, Team)

    def get_by_name(self, name: str) -> Team | None:
        """
        Obtiene un equipo por su nombre.

        Args:
            name (str): Nombre del equipo.

        Returns:
            Team | None: Instancia encontrada o None si no existe.

        """
        return self.session.exec(
            select(Team).where(Team.name == name)
        ).first()

    def get_active(self, offset: int = 0, limit: int = 20) -> list[Team]:
        """
        Obtiene equipos activos con paginación.

        Args:
            offset (int): Cantidad de registros a omitir.
            limit (int): Máximo de registros a devolver.

        Returns:
            list[Team]: Lista de equipos activos.

        Nota:
            - No se define orden explícito → resultados no determinísticos
            - Se usa '== True' por compatibilidad con el ORM
        """
        return list(
            self.session.exec(
                select(Team)
                .where(Team.is_active == True)  # noqa: E712
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count(self) -> int:
        """
        Cuenta la cantidad total de equipos.

        Returns:
            int: Total de registros en la tabla Team.
        """
        return len(self.session.exec(select(Team)).all())