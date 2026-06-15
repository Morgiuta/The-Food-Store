from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import cloudinary

from app.api.router import api_router
from app.api.error_handlers import register_error_handlers
from app.core.database import create_db_and_tables
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    yield


app = FastAPI(
    title="Catalogo de Productos API",
    description="Backend del dominio Catalogo de Productos con FastAPI y SQLModel",
    version="1.0.0",
    lifespan=lifespan,
)

register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
