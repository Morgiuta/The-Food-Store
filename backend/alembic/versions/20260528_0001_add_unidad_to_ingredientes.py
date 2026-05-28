"""add unidad to ingredientes

Revision ID: 20260528_0001
Revises: 194ea7ae7ae2
Create Date: 2026-05-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260528_0001"
down_revision = "194ea7ae7ae2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ingredientes",
        sa.Column(
            "unidad",
            sa.String(length=20),
            nullable=False,
            server_default="unidad",
        ),
    )


def downgrade() -> None:
    op.drop_column("ingredientes", "unidad")
