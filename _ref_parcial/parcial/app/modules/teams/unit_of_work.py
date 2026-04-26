from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.teams.repository import TeamRepository
from app.modules.heroes.repository import HeroRepository


class TeamUnitOfWork(UnitOfWork):
    """
    UoW del módulo teams.
    Expone tanto TeamRepository como HeroRepository porque
    asignar héroes a un equipo toca ambas entidades en la misma transacción.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.teams = TeamRepository(session)
        self.heroes = HeroRepository(session)  # cross-module, misma transacción
