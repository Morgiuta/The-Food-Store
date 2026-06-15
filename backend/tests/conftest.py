import pytest
import anyio
import anyio.to_thread
import httpx
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


async def run_sync_inline(func, *args, **kwargs):
    kwargs.pop("abandon_on_cancel", None)
    kwargs.pop("cancellable", None)
    kwargs.pop("limiter", None)
    return func(*args, **kwargs)


anyio.to_thread.run_sync = run_sync_inline


class ASGITestClient:
    def __init__(self, app):
        self.app = app

    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        async def send_request() -> httpx.Response:
            transport = httpx.ASGITransport(app=self.app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as client:
                return await client.request(method, url, **kwargs)

        return anyio.run(send_request)

    def get(self, url: str, **kwargs) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> httpx.Response:
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs) -> httpx.Response:
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs) -> httpx.Response:
        return self.request("DELETE", url, **kwargs)


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
        
        from app.modules.unidad_medida.models import UnidadMedida
        unidad = session.exec(select(UnidadMedida).where(UnidadMedida.id == 1)).first()
        if not unidad:
            unidad = UnidadMedida(id=1, codigo="KG", nombre="Kilogramo", simbolo="kg")
            session.add(unidad)
            session.commit()
        session.commit()

    def get_session_override():
        return session

    def get_current_user_override():
        return admin_user

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    yield ASGITestClient(app)

    app.dependency_overrides.clear()
