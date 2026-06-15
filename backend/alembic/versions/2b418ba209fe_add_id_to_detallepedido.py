"""Add id to DetallePedido

Revision ID: 2b418ba209fe
Revises: 75f2196c70df
Create Date: 2026-06-15 17:40:19.189088
"""

from alembic import op
import sqlalchemy as sa



revision = '2b418ba209fe'
down_revision = '75f2196c70df'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint('detalle_pedidos_pkey', 'detalle_pedidos', type_='primary')
    op.execute('ALTER TABLE detalle_pedidos ADD COLUMN id BIGSERIAL PRIMARY KEY')


def downgrade() -> None:
    op.drop_column('detalle_pedidos', 'id')
    op.create_primary_key('detalle_pedidos_pkey', 'detalle_pedidos', ['pedido_id', 'producto_id'])
