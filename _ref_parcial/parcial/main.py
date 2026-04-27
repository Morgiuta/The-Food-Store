from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import create_db_and_tables
from app.modules.health.router import router as health_router
from app.modules.heroes.router import router as heroes_router
from app.modules.teams.router import router as teams_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Team Hero API",
    description="Ejemplo de arquitectura Router → Service → UoW → Repository",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(heroes_router, prefix="/heroes", tags=["heroes"])
app.include_router(teams_router, prefix="/teams", tags=["teams"])
