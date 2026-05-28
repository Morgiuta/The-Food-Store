"""add es_producto_terminado to ingredientes

Revision ID: 20260528_0002
Revises: 20260528_0001
Create Date: 2026-05-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260528_0002"
down_revision = "20260528_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ingredientes",
        sa.Column(
            "es_producto_terminado",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("ingredientes", "es_producto_terminado")
