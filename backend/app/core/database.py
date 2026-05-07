from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine = create_engine(settings.database_url, echo=False)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    ensure_ingrediente_soft_delete_column()


def ensure_ingrediente_soft_delete_column() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("ingredientes"):
        return

    columns = {column["name"] for column in inspector.get_columns("ingredientes")}
    if "deleted_at" in columns:
        return

    column_type = (
        "TIMESTAMP WITH TIME ZONE"
        if engine.dialect.name == "postgresql"
        else "DATETIME"
    )
    with engine.begin() as connection:
        connection.execute(text(f"ALTER TABLE ingredientes ADD COLUMN deleted_at {column_type}"))


def get_session():
    with Session(engine) as session:
        yield session
