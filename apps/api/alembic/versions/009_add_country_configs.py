"""add country configs table

Revision ID: 009
Revises: 008
Create Date: 2025-12-14 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create country_configs table
    op.create_table(
        'country_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('country_code', sa.String(length=2), nullable=False),
        sa.Column('country_name', sa.String(length=100), nullable=False),
        sa.Column('default_currency', sa.String(length=3), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False),
        sa.Column('working_hours_per_week', sa.Numeric(precision=5, scale=2), nullable=False, server_default='40'),
        sa.Column('working_days_per_week', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('public_holidays', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('country_code')
    )
    op.create_index(op.f('ix_country_configs_country_code'), 'country_configs', ['country_code'], unique=False)

    # Create salary_bands table
    op.create_table(
        'salary_bands',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('country_code', sa.String(length=2), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('min_salary', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('max_salary', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('currency_code', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_salary_bands_country_code'), 'salary_bands', ['country_code'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_salary_bands_country_code'), table_name='salary_bands')
    op.drop_table('salary_bands')
    op.drop_index(op.f('ix_country_configs_country_code'), table_name='country_configs')
    op.drop_table('country_configs')
