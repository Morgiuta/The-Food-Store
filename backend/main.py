from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Catalogo de Productos API",
    description="Backend del dominio Catalogo de Productos con FastAPI y SQLModel",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(api_router)
