"""Add missing index on employees.user_id for performance

Revision ID: 017_add_user_id_index
Revises: 016_add_multi_level_approvals
Create Date: 2026-01-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '017_add_user_id_index'
down_revision = '016_add_multi_level_approvals'
branch_labels = None
depends_on = None


def upgrade():
    """Add index on employees.user_id for faster lookups"""
    # Create index if it doesn't exist (safe operation, no data changes)
    conn = op.get_bind()
    conn.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS idx_employees_user_id 
        ON employees (user_id)
        WHERE user_id IS NOT NULL
    """))


def downgrade():
    """Remove index on employees.user_id"""
    op.drop_index('idx_employees_user_id', 'employees')
