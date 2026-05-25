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
from app.modules.direcciones.models import Direccion  # noqa: F401
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
    normalize_pedido_estado_codes()
    ensure_ingrediente_soft_delete_column()
    migrate_direcciones_to_direcciones_entrega()
    ensure_direcciones_usuario_fk()
    ensure_pedido_direccion_fk()
    ensure_historial_estado_append_only()


def ensure_auth_tables() -> None:
    inspector = inspect(engine)
    required_tables = {
        "roles",
        "usuarios",
        "usuario_roles",
        "refresh_tokens",
        "direcciones_entrega",
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

    def table_columns(table_name: str) -> set[str]:
        if not inspector.has_table(table_name):
            return set()
        return {column["name"] for column in inspector.get_columns(table_name)}

    roles_columns = table_columns("roles")
    users_columns = table_columns("users")
    user_roles_columns = table_columns("user_roles")
    legacy_roles_table = {"name", "description"}.issubset(roles_columns)
    legacy_users_table = {"username", "hashed_password"}.issubset(users_columns)
    legacy_user_roles_table = {"user_id", "role_id"}.issubset(user_roles_columns)
    existing_legacy_tables = {
        table_name
        for table_name in ("permissions", "role_permissions")
        if inspector.has_table(table_name)
    }
    if legacy_roles_table:
        existing_legacy_tables.add("roles")
    if legacy_users_table:
        existing_legacy_tables.add("users")
    if legacy_user_roles_table:
        existing_legacy_tables.add("user_roles")

    if not existing_legacy_tables:
        return

    SQLModel.metadata.create_all(engine)

    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            if legacy_roles_table:
                connection.execute(
                    text(
                        """
                        INSERT INTO roles (codigo, nombre, descripcion)
                        SELECT UPPER(name), name, description
                        FROM roles
                        ON CONFLICT (codigo) DO NOTHING
                        """
                    )
                )

            if legacy_users_table:
                connection.execute(
                    text(
                        """
                        INSERT INTO roles (codigo, nombre, descripcion)
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
                        INSERT INTO usuarios
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
                            pg_get_serial_sequence('usuarios', 'id'),
                            COALESCE((SELECT MAX(id) FROM usuarios), 1),
                            true
                        )
                        """
                    )
                )

            if legacy_users_table and legacy_roles_table and legacy_user_roles_table:
                connection.execute(
                    text(
                        """
                        INSERT INTO usuario_roles (usuario_id, rol_codigo, created_at)
                        SELECT ur.user_id, UPPER(r.name), CURRENT_TIMESTAMP
                        FROM user_roles ur
                        JOIN roles r ON r.id = ur.role_id
                        ON CONFLICT (usuario_id, rol_codigo) DO NOTHING
                        """
                    )
                )

            if legacy_users_table:
                connection.execute(
                    text(
                        """
                        INSERT INTO usuario_roles (usuario_id, rol_codigo, created_at)
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
        "usuarios": ("created_at", "updated_at", "deleted_at"),
        "usuario_roles": ("created_at", "expires_at"),
        "refresh_tokens": ("created_at", "expires_at", "revoked_at"),
        "direcciones_entrega": ("created_at", "updated_at", "deleted_at"),
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
                        ALTER TABLE {table_name}
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


def ensure_pedido_direccion_fk() -> None:
    if engine.dialect.name != "postgresql":
        return

    inspector = inspect(engine)
    if not inspector.has_table("pedidos") or not inspector.has_table("direcciones_entrega"):
        return

    direccion_fks = [
        fk
        for fk in inspector.get_foreign_keys("pedidos")
        if fk.get("constrained_columns") == ["direccion_id"]
    ]
    if any(fk.get("referred_table") == "direcciones_entrega" for fk in direccion_fks):
        return

    with engine.begin() as connection:
        for fk in direccion_fks:
            constraint_name = fk.get("name")
            if constraint_name:
                connection.execute(
                    text(f"ALTER TABLE pedidos DROP CONSTRAINT IF EXISTS {constraint_name}")
                )

        connection.execute(
            text(
                """
                ALTER TABLE pedidos
                ADD CONSTRAINT pedidos_direccion_id_fkey
                FOREIGN KEY (direccion_id)
                REFERENCES direcciones_entrega(id)
                ON DELETE SET NULL
                NOT VALID
                """
            )
        )


def normalize_pedido_estado_codes() -> None:
    if engine.dialect.name != "postgresql":
        return

    inspector = inspect(engine)
    required_tables = {
        "estados_pedido",
        "pedidos",
        "historial_estados_pedido",
    }
    if any(not inspector.has_table(table_name) for table_name in required_tables):
        return

    with engine.begin() as connection:
        connection.execute(
            text("UPDATE pedidos SET estado_codigo = 'EN_PREP' WHERE estado_codigo = 'EN_PROCESO'")
        )
        connection.execute(
            text("UPDATE pedidos SET estado_codigo = 'EN_CAMINO' WHERE estado_codigo = 'LISTO'")
        )
        connection.execute(
            text(
                """
                UPDATE historial_estados_pedido
                SET estado_desde = 'EN_PREP'
                WHERE estado_desde = 'EN_PROCESO'
                """
            )
        )
        connection.execute(
            text(
                """
                UPDATE historial_estados_pedido
                SET estado_hacia = 'EN_PREP'
                WHERE estado_hacia = 'EN_PROCESO'
                """
            )
        )
        connection.execute(
            text(
                """
                UPDATE historial_estados_pedido
                SET estado_desde = 'EN_CAMINO'
                WHERE estado_desde = 'LISTO'
                """
            )
        )
        connection.execute(
            text(
                """
                UPDATE historial_estados_pedido
                SET estado_hacia = 'EN_CAMINO'
                WHERE estado_hacia = 'LISTO'
                """
            )
        )
        connection.execute(text("DELETE FROM estados_pedido WHERE codigo IN ('EN_PROCESO', 'LISTO')"))


def migrate_direcciones_to_direcciones_entrega() -> None:
    if engine.dialect.name != "postgresql":
        return

    inspector = inspect(engine)
    if not inspector.has_table("direcciones") or not inspector.has_table("direcciones_entrega"):
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO direcciones_entrega
                    (
                        id,
                        usuario_id,
                        alias,
                        linea1,
                        linea2,
                        ciudad,
                        provincia,
                        codigo_postal,
                        es_principal,
                        created_at,
                        updated_at,
                        deleted_at
                    )
                SELECT
                    d.id,
                    d.usuario_id,
                    NULL,
                    d.calle,
                    d.numero,
                    d.ciudad,
                    d.provincia,
                    d.codigo_postal,
                    d.es_principal,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP,
                    d.deleted_at
                FROM direcciones d
                ON CONFLICT (id) DO NOTHING
                """
            )
        )
        connection.execute(
            text(
                """
                SELECT setval(
                    pg_get_serial_sequence('direcciones_entrega', 'id'),
                    COALESCE((SELECT MAX(id) FROM direcciones_entrega), 1),
                    true
                )
                """
            )
        )


def ensure_direcciones_usuario_fk() -> None:
    if engine.dialect.name != "postgresql":
        return

    inspector = inspect(engine)
    if not inspector.has_table("direcciones") or not inspector.has_table("usuarios"):
        return

    usuario_fks = [
        fk
        for fk in inspector.get_foreign_keys("direcciones")
        if fk.get("constrained_columns") == ["usuario_id"]
    ]
    if any(fk.get("referred_table") == "usuarios" for fk in usuario_fks):
        return

    with engine.begin() as connection:
        for fk in usuario_fks:
            constraint_name = fk.get("name")
            if constraint_name:
                connection.execute(
                    text(f"ALTER TABLE direcciones DROP CONSTRAINT IF EXISTS {constraint_name}")
                )

        connection.execute(
            text(
                """
                ALTER TABLE direcciones
                ADD CONSTRAINT direcciones_usuario_id_fkey
                FOREIGN KEY (usuario_id)
                REFERENCES usuarios(id)
                NOT VALID
                """
            )
        )


def ensure_historial_estado_append_only() -> None:
    if engine.dialect.name != "postgresql":
        return

    inspector = inspect(engine)
    if not inspector.has_table("historial_estados_pedido"):
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE OR REPLACE FUNCTION prevent_historial_estados_pedido_mutation()
                RETURNS trigger AS $$
                BEGIN
                    RAISE EXCEPTION
                        'historial_estados_pedido is append-only; UPDATE and DELETE are not allowed';
                END;
                $$ LANGUAGE plpgsql;
                """
            )
        )
        connection.execute(
            text(
                """
                DROP TRIGGER IF EXISTS trg_historial_estados_pedido_append_only
                ON historial_estados_pedido;
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TRIGGER trg_historial_estados_pedido_append_only
                BEFORE UPDATE OR DELETE ON historial_estados_pedido
                FOR EACH ROW
                EXECUTE FUNCTION prevent_historial_estados_pedido_mutation();
                """
            )
        )


def get_session():
    with Session(engine) as session:
        yield session
