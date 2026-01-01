"""Add tenant support to payrolls

Revision ID: 008
Revises: 007
Create Date: 2025-12-14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    """Add country_code column to payrolls table for multi-tenant support"""
    
    # Add country_code column to payrolls table
    op.add_column('payrolls', sa.Column('country_code', sa.String(length=2), nullable=True))
    
    # Add index for better query performance
    op.create_index('ix_payrolls_country_code', 'payrolls', ['country_code'])
    
    # Add index for common query pattern (month, year, country_code)
    op.create_index('ix_payrolls_period_tenant', 'payrolls', ['month', 'year', 'country_code'])


def downgrade():
    """Remove tenant support from payrolls table"""
    
    # Drop indexes
    op.drop_index('ix_payrolls_period_tenant', 'payrolls')
    op.drop_index('ix_payrolls_country_code', 'payrolls')
    
    # Drop column
    op.drop_column('payrolls', 'country_code')
