"""Add index on employment_type for faster filtering

Revision ID: 019_add_employment_type_index
Revises: 018_add_employee_additional_fields
Create Date: 2026-01-04 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '019_add_employment_type_index'
down_revision = '018_add_employee_additional_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add index on employment_type for faster filtering"""
    # Create index if it doesn't exist (safe operation, no data changes)
    conn = op.get_bind()
    conn.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS idx_employees_employment_type 
        ON employees (employment_type)
        WHERE is_deleted = false
    """))


def downgrade():
    """Remove index on employment_type"""
    op.drop_index('idx_employees_employment_type', 'employees')
