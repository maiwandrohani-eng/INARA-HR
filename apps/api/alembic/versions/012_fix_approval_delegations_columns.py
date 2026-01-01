"""fix approval_delegations table columns

Revision ID: 012
Revises: 011
Create Date: 2025-12-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to approval_delegations table
    # These columns should be present due to BaseModel (SoftDeleteMixin) and TenantMixin
    op.add_column('approval_delegations', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('approval_delegations', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('approval_delegations', sa.Column('country_code', sa.String(length=5), nullable=True))


def downgrade():
    op.drop_column('approval_delegations', 'country_code')
    op.drop_column('approval_delegations', 'deleted_at')
    op.drop_column('approval_delegations', 'is_deleted')

