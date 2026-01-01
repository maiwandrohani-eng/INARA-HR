"""Add multi-level approval support

Revision ID: 016_add_multi_level_approvals
Revises: 015_add_remaining_modules
Create Date: 2026-01-01 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '016_add_multi_level_approvals'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade():
    # Add approval level and chain tracking to approval_requests
    op.add_column('approval_requests', sa.Column('approval_level', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('approval_requests', sa.Column('previous_approval_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('approval_requests', sa.Column('is_final_approval', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('approval_requests', sa.Column('next_approver_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_approval_requests_previous_approval',
        'approval_requests', 'approval_requests',
        ['previous_approval_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_approval_requests_next_approver',
        'approval_requests', 'employees',
        ['next_approver_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Add approval types for payroll, safeguarding, grievance, workforce
    # Note: This requires updating the enum in the code, but PostgreSQL enum changes need special handling
    # We'll handle the enum update in the model definition
    
    # Add payroll approval tracking
    op.add_column('payrolls', sa.Column('finance_reviewed_at', sa.DateTime(), nullable=True))
    op.add_column('payrolls', sa.Column('finance_reviewed_by_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('payrolls', sa.Column('ceo_approved_at', sa.DateTime(), nullable=True))
    op.add_column('payrolls', sa.Column('ceo_approved_by_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_payrolls_finance_reviewer',
        'payrolls', 'users',
        ['finance_reviewed_by_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_payrolls_ceo_approver',
        'payrolls', 'users',
        ['ceo_approved_by_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    op.drop_constraint('fk_payrolls_ceo_approver', 'payrolls', type_='foreignkey')
    op.drop_constraint('fk_payrolls_finance_reviewer', 'payrolls', type_='foreignkey')
    op.drop_column('payrolls', 'ceo_approved_by_id')
    op.drop_column('payrolls', 'ceo_approved_at')
    op.drop_column('payrolls', 'finance_reviewed_by_id')
    op.drop_column('payrolls', 'finance_reviewed_at')
    
    op.drop_constraint('fk_approval_requests_next_approver', 'approval_requests', type_='foreignkey')
    op.drop_constraint('fk_approval_requests_previous_approval', 'approval_requests', type_='foreignkey')
    op.drop_column('approval_requests', 'next_approver_id')
    op.drop_column('approval_requests', 'is_final_approval')
    op.drop_column('approval_requests', 'previous_approval_id')
    op.drop_column('approval_requests', 'approval_level')

