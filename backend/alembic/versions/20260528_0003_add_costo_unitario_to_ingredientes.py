from alembic import op
import sqlalchemy as sa


revision = '20260528_0003'
down_revision = '20260528_0002'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ingredientes', sa.Column('costo_unitario', sa.Numeric(10, 2), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('ingredientes', 'costo_unitario')
