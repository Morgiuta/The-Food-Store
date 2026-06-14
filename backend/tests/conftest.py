import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import BigInteger

@compiles(BigInteger, 'sqlite')
def compile_big_int_sqlite(type_, compiler, **kw):
    return 'INTEGER'

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

import app.core.database
app.core.database.engine = engine

from main import app
from app.core.database import get_session, create_db_and_tables
from app.modules.auth.models import Usuario, UsuarioRol
from app.modules.auth.dependencies import get_current_user

@pytest.fixture(name="session")
def session_fixture():
    create_db_and_tables()
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    admin_user = session.exec(select(Usuario).where(Usuario.email == "admin@test.com")).first()
    if not admin_user:
        admin_user = Usuario(
            nombre="Admin",
            apellido="Prueba",
            email="admin@test.com",
            password_hash="hash_simulado"
        )
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)

        session.add(UsuarioRol(usuario_id=admin_user.id, rol_codigo="ADMIN"))
        session.commit()

    def get_session_override():
        return session

    def get_current_user_override():
        return admin_user

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override
    
    with TestClient(app) as client:
        yield client
        
    app.dependency_overrides.clear()