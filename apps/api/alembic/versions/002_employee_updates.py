"""Make date_of_birth nullable and add country_code

Revision ID: 002
Revises: 001
Create Date: 2024-12-07 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Make date_of_birth nullable and add country_code column"""
    # Make date_of_birth nullable
    op.alter_column('employees', 'date_of_birth',
                    existing_type=sa.Date(),
                    nullable=True)
    
    # Add country_code column if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'employees' AND column_name = 'country_code'
            ) THEN
                ALTER TABLE employees ADD COLUMN country_code VARCHAR(2);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Revert changes"""
    # Make date_of_birth non-nullable
    op.alter_column('employees', 'date_of_birth',
                    existing_type=sa.Date(),
                    nullable=False)
    
    # Remove country_code column
    op.drop_column('employees', 'country_code')
