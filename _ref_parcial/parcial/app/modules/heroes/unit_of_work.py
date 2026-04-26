from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.heroes.repository import HeroRepository
from app.modules.teams.repository import TeamRepository

class HeroUnitOfWork(UnitOfWork):
    """
    UoW específico del módulo heroes.
    Expone los repositorios que el servicio necesita coordinar.

    Al entrar al contexto (with uow:) todos los repositorios
    comparten la misma Session → misma transacción.
    """

    def __init__(self, session: Session) -> None:
        """
    UnitOfWork específico del dominio Hero.

    Extiende el UnitOfWork base y registra los repositorios necesarios
    para operar dentro de una misma transacción consistente.

    Repositorios expuestos:
        - heroes: acceso a operaciones sobre Hero
        - teams: acceso a operaciones sobre Team (usado para validaciones
                 de integridad antes de persistir héroes)

    Args:
        session (Session): Sesión activa de base de datos compartida
                           por todos los repositorios.

    Responsabilidad:
        - Garantizar que todas las operaciones (Hero, Team, etc.)
          se ejecuten dentro de la misma transacción
        - Centralizar commit() y rollback() (heredado del UoW base)
        - Coordinar múltiples repositorios bajo una única unidad de trabajo

    Uso típico:

        with HeroUnitOfWork(session) as uow:
            team = uow.teams.get_by_id(team_id)
            hero = Hero(...)
            uow.heroes.add(hero)
        """
        super().__init__(session)
        self.heroes = HeroRepository(session)
        self.teams = TeamRepository(session)
