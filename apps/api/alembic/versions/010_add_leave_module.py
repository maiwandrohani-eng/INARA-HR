"""add leave module tables

Revision ID: 010
Revises: 009
Create Date: 2025-12-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade():
    # Create leave_policies table
    op.create_table(
        'leave_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('leave_type', sa.String(length=50), nullable=False),
        sa.Column('days_per_year', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('accrual_rate', sa.String(length=20), nullable=True),
        sa.Column('max_carryover', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_leave_policies_country_code', 'leave_policies', ['country_code'])
    op.create_index('ix_leave_policies_leave_type', 'leave_policies', ['leave_type'])

    # Create leave_balances table
    op.create_table(
        'leave_balances',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('leave_type', sa.String(length=50), nullable=False),
        sa.Column('year', sa.String(length=10), nullable=False),
        sa.Column('total_days', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('used_days', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('pending_days', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0'),
        sa.Column('available_days', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_leave_balances_employee_id', 'leave_balances', ['employee_id'])
    op.create_index('ix_leave_balances_year', 'leave_balances', ['year'])

    # Create leave_requests table
    op.create_table(
        'leave_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('leave_type', sa.String(length=50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('total_days', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('approver_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_date', sa.Date(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('supporting_document_url', sa.String(length=500), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['approver_id'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_leave_requests_employee_id', 'leave_requests', ['employee_id'])
    op.create_index('ix_leave_requests_status', 'leave_requests', ['status'])
    op.create_index('ix_leave_requests_start_date', 'leave_requests', ['start_date'])

    # Create attendance_records table
    op.create_table(
        'attendance_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('check_in_time', sa.String(length=20), nullable=True),
        sa.Column('check_out_time', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='present'),
        sa.Column('work_hours', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_attendance_records_employee_id', 'attendance_records', ['employee_id'])
    op.create_index('ix_attendance_records_date', 'attendance_records', ['date'])


def downgrade():
    op.drop_table('attendance_records')
    op.drop_table('leave_requests')
    op.drop_table('leave_balances')
    op.drop_table('leave_policies')
