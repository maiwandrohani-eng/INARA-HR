"""
Alembic Migration: Add approval workflow tables

Revision ID: 003
Revises: 002
Create Date: 2024
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create approval_requests table
    op.create_table(
        'approval_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('request_type', sa.String(50), nullable=False),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Create indexes for approval_requests
    op.create_index('ix_approval_requests_employee_id', 'approval_requests', ['employee_id'])
    op.create_index('ix_approval_requests_approver_id', 'approval_requests', ['approver_id'])
    op.create_index('ix_approval_requests_status', 'approval_requests', ['status'])
    op.create_index('ix_approval_requests_type', 'approval_requests', ['request_type'])
    
    # Create approval_delegations table
    op.create_table(
        'approval_delegations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('supervisor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('delegate_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.String(10), nullable=False, server_default='true'),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Create indexes for approval_delegations
    op.create_index('ix_approval_delegations_supervisor_id', 'approval_delegations', ['supervisor_id'])
    op.create_index('ix_approval_delegations_delegate_id', 'approval_delegations', ['delegate_id'])
    op.create_index('ix_approval_delegations_active', 'approval_delegations', ['is_active'])


def downgrade():
    # Drop approval_delegations table
    op.drop_index('ix_approval_delegations_active', table_name='approval_delegations')
    op.drop_index('ix_approval_delegations_delegate_id', table_name='approval_delegations')
    op.drop_index('ix_approval_delegations_supervisor_id', table_name='approval_delegations')
    op.drop_table('approval_delegations')
    
    # Drop approval_requests table
    op.drop_index('ix_approval_requests_type', table_name='approval_requests')
    op.drop_index('ix_approval_requests_status', table_name='approval_requests')
    op.drop_index('ix_approval_requests_approver_id', table_name='approval_requests')
    op.drop_index('ix_approval_requests_employee_id', table_name='approval_requests')
    op.drop_table('approval_requests')
