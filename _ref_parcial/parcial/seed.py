"""
Script de seed para desarrollo.
Ejecutar: python seed.py
Crea datos de prueba para demostrar el flujo completo.
"""
from sqlmodel import Session
from app.core.database import engine, create_db_and_tables
from app.modules.heroes.models import Hero
from app.modules.teams.models import Team


def seed() -> None:
    create_db_and_tables()

    with Session(engine) as session:
        # Equipos
        avengers = Team(name="Avengers", headquarters="Stark Tower, New York")
        xmen = Team(name="X-Men", headquarters="Xavier Institute, Westchester")
        session.add(avengers)
        session.add(xmen)
        session.flush()

        # Héroes con equipo asignado
        heroes = [
            Hero(name="Steve Rogers",   alias="Captain America", power_level=88, team_id=avengers.id),
            Hero(name="Tony Stark",     alias="Iron Man",        power_level=95, team_id=avengers.id),
            Hero(name="Natasha R.",     alias="Black Widow",     power_level=80, team_id=avengers.id),
            Hero(name="Scott Summers",  alias="Cyclops",         power_level=82, team_id=xmen.id),
            Hero(name="Jean Grey",      alias="Phoenix",         power_level=98, team_id=xmen.id),
            # Sin equipo por ahora
            Hero(name="Peter Parker",   alias="Spider-Man",      power_level=85),
        ]
        for hero in heroes:
            session.add(hero)

        session.commit()
        print(f"Seed OK: {len(heroes)} héroes, 2 equipos creados.")


if __name__ == "__main__":
    seed()
