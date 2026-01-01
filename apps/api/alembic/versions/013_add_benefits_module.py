"""add benefits management module tables

Revision ID: 013
Revises: 012
Create Date: 2025-12-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade():
    # Create benefit_plans table
    op.create_table(
        'benefit_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('benefit_type', sa.String(length=50), nullable=False),
        sa.Column('provider', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('coverage_start_date', sa.Date(), nullable=True),
        sa.Column('coverage_end_date', sa.Date(), nullable=True),
        sa.Column('eligibility_criteria', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('employer_contribution_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('employer_contribution_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('employee_cost_per_pay_period', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_benefit_plans_benefit_type', 'benefit_plans', ['benefit_type'])
    op.create_index('ix_benefit_plans_country_code', 'benefit_plans', ['country_code'])

    # Create benefit_enrollments table
    op.create_table(
        'benefit_enrollments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('benefit_plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('enrollment_date', sa.Date(), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('coverage_level', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='active'),
        sa.Column('dependents_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('employee_contribution_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['benefit_plan_id'], ['benefit_plans.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_benefit_enrollments_employee_id', 'benefit_enrollments', ['employee_id'])
    op.create_index('ix_benefit_enrollments_status', 'benefit_enrollments', ['status'])

    # Create benefit_dependents table
    op.create_table(
        'benefit_dependents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('enrollment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('dependent_relationship', sa.String(length=50), nullable=False),
        sa.Column('ssn', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('coverage_start_date', sa.Date(), nullable=True),
        sa.Column('coverage_end_date', sa.Date(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['enrollment_id'], ['benefit_enrollments.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_benefit_dependents_enrollment_id', 'benefit_dependents', ['enrollment_id'])

    # Create open_enrollment_periods table
    op.create_table(
        'open_enrollment_periods',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('applicable_benefit_types', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_open_enrollment_periods_year', 'open_enrollment_periods', ['year'])


def downgrade():
    op.drop_index('ix_open_enrollment_periods_year', table_name='open_enrollment_periods')
    op.drop_table('open_enrollment_periods')
    
    op.drop_index('ix_benefit_dependents_enrollment_id', table_name='benefit_dependents')
    op.drop_table('benefit_dependents')
    
    op.drop_index('ix_benefit_enrollments_status', table_name='benefit_enrollments')
    op.drop_index('ix_benefit_enrollments_employee_id', table_name='benefit_enrollments')
    op.drop_table('benefit_enrollments')
    
    op.drop_index('ix_benefit_plans_country_code', table_name='benefit_plans')
    op.drop_index('ix_benefit_plans_benefit_type', table_name='benefit_plans')
    op.drop_table('benefit_plans')

