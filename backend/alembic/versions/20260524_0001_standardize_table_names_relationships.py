"""standardize table names and soft delete columns

Revision ID: 20260524_0001
Revises:
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa


revision = "20260524_0001"
down_revision = None
branch_labels = None
depends_on = None


TABLE_RENAMES = {
    "Rol": "roles",
    "Usuario": "usuarios",
    "UsuarioRol": "usuario_roles",
    "RefreshToken": "refresh_tokens",
    "DireccionEntrega": "direcciones_entrega",
    "FormaPago": "formas_pago",
    "EstadoPedido": "estados_pedido",
    "Pedido": "pedidos",
    "Pago": "pagos",
    "HistorialEstadoPedido": "historial_estados_pedido",
    "DetallePedido": "detalle_pedidos",
}


def _has_table(inspector, table_name: str) -> bool:
    return inspector.has_table(table_name)


def _has_column(inspector, table_name: str, column_name: str) -> bool:
    if not _has_table(inspector, table_name):
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for old_name, new_name in TABLE_RENAMES.items():
        if _has_table(inspector, old_name) and not _has_table(inspector, new_name):
            op.rename_table(old_name, new_name)
            inspector = sa.inspect(bind)

    for table_name in ("formas_pago", "pagos", "detalle_pedidos"):
        if _has_table(inspector, table_name) and not _has_column(
            inspector,
            table_name,
            "deleted_at",
        ):
            op.add_column(
                table_name,
                sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            )
            inspector = sa.inspect(bind)


def downgrade() -> None:
    pass
