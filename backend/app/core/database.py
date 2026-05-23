from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.modules.auth.models import (  # noqa: F401
    DireccionEntrega,
    RefreshToken,
    Rol,
    Usuario,
    UsuarioRol,
)
from app.modules.categoria.models import Categoria  # noqa: F401
from app.modules.ingrediente.models import Ingrediente  # noqa: F401
from app.modules.producto.models import Producto  # noqa: F401
from app.modules.producto_categoria.models import ProductoCategoria  # noqa: F401
from app.modules.producto_ingrediente.models import ProductoIngrediente  # noqa: F401
from app.modules.ventas.models import (  # noqa: F401
    DetallePedido,
    EstadoPedido,
    FormaPago,
    HistorialEstadoPedido,
    Pago,
    Pedido,
)
from app.core.seed import seed_required_data

engine = create_engine(settings.database_url, echo=False)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    migrate_legacy_auth_tables()
    ensure_auth_tables()
    ensure_auth_timestamp_columns()
    seed_formal_data()
    ensure_ingrediente_soft_delete_column()


def ensure_auth_tables() -> None:
    inspector = inspect(engine)
    required_tables = {
        "Rol",
        "Usuario",
        "UsuarioRol",
        "RefreshToken",
        "DireccionEntrega",
    }
    missing_tables = [
        table_name
        for table_name in required_tables
        if not inspector.has_table(table_name)
    ]
    if not missing_tables:
        return

    SQLModel.metadata.create_all(engine)


def migrate_legacy_auth_tables() -> None:
    inspector = inspect(engine)
    legacy_tables = {"users", "roles", "user_roles", "permissions", "role_permissions"}
    existing_legacy_tables = {
        table_name for table_name in legacy_tables if inspector.has_table(table_name)
    }
    if not existing_legacy_tables:
        return

    SQLModel.metadata.create_all(engine)

    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            if "roles" in existing_legacy_tables:
                connection.execute(
                    text(
                        """
                        INSERT INTO "Rol" (codigo, nombre, descripcion)
                        SELECT UPPER(name), name, description
                        FROM roles
                        ON CONFLICT (codigo) DO NOTHING
                        """
                    )
                )

            if "users" in existing_legacy_tables:
                connection.execute(
                    text(
                        """
                        INSERT INTO "Rol" (codigo, nombre, descripcion)
                        SELECT DISTINCT UPPER(role), UPPER(role), 'Rol ' || UPPER(role)
                        FROM users
                        WHERE role IS NOT NULL
                        ON CONFLICT (codigo) DO NOTHING
                        """
                    )
                )
                connection.execute(
                    text(
                        """
                        INSERT INTO "Usuario"
                            (id, nombre, apellido, email, password_hash, created_at, updated_at)
                        SELECT
                            id,
                            COALESCE(NULLIF(split_part(full_name, ' ', 1), ''), username),
                            COALESCE(NULLIF(substr(full_name, length(split_part(full_name, ' ', 1)) + 2), ''), '-'),
                            username,
                            hashed_password,
                            created_at,
                            updated_at
                        FROM users
                        ON CONFLICT (email) DO NOTHING
                        """
                    )
                )
                connection.execute(
                    text(
                        """
                        SELECT setval(
                            pg_get_serial_sequence('"Usuario"', 'id'),
                            COALESCE((SELECT MAX(id) FROM "Usuario"), 1),
                            true
                        )
                        """
                    )
                )

            if {"users", "roles", "user_roles"}.issubset(existing_legacy_tables):
                connection.execute(
                    text(
                        """
                        INSERT INTO "UsuarioRol" (usuario_id, rol_codigo, created_at)
                        SELECT ur.user_id, UPPER(r.name), CURRENT_TIMESTAMP
                        FROM user_roles ur
                        JOIN roles r ON r.id = ur.role_id
                        ON CONFLICT (usuario_id, rol_codigo) DO NOTHING
                        """
                    )
                )

            if "users" in existing_legacy_tables:
                connection.execute(
                    text(
                        """
                        INSERT INTO "UsuarioRol" (usuario_id, rol_codigo, created_at)
                        SELECT u.id, UPPER(u.role), CURRENT_TIMESTAMP
                        FROM users u
                        WHERE u.role IS NOT NULL
                        ON CONFLICT (usuario_id, rol_codigo) DO NOTHING
                        """
                    )
                )

            connection.execute(
                text(
                    """
                    DROP TABLE IF EXISTS
                        role_permissions,
                        permissions,
                        user_roles,
                        roles,
                        users
                    CASCADE
                    """
                )
            )


def ensure_auth_timestamp_columns() -> None:
    if engine.dialect.name != "postgresql":
        return

    timestamp_columns = {
        "Usuario": ("created_at", "updated_at", "deleted_at"),
        "UsuarioRol": ("created_at", "expires_at"),
        "RefreshToken": ("created_at", "expires_at", "revoked_at"),
        "DireccionEntrega": ("created_at", "updated_at", "deleted_at"),
    }

    with engine.begin() as connection:
        for table_name, columns in timestamp_columns.items():
            for column_name in columns:
                column_type = connection.execute(
                    text(
                        """
                        SELECT data_type
                        FROM information_schema.columns
                        WHERE table_name = :table_name
                          AND column_name = :column_name
                        """
                    ),
                    {"table_name": table_name, "column_name": column_name},
                ).scalar_one_or_none()
                if column_type == "timestamp with time zone":
                    continue

                connection.execute(
                    text(
                        f"""
                        ALTER TABLE "{table_name}"
                        ALTER COLUMN {column_name}
                        TYPE TIMESTAMP WITH TIME ZONE
                        USING {column_name} AT TIME ZONE 'UTC'
                        """
                    )
                )


def seed_formal_data() -> None:
    with Session(engine) as session:
        seed_required_data(session)


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
