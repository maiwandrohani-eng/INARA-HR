"""Add payroll module

Revision ID: 007
Revises: 006
Create Date: 2025-12-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    """Add payroll tables"""
    
    # Create PayrollStatus enum if not exists
    conn = op.get_bind()
    conn.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE payrollstatus AS ENUM ('DRAFT', 'PENDING_FINANCE', 'PENDING_CEO', 'APPROVED', 'REJECTED', 'PROCESSED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))
    
    # Create payrolls table
    op.create_table(
        'payrolls',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('payment_date', sa.DateTime(), nullable=False),
        sa.Column('total_basic_salary', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('total_allowances', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('total_gross_salary', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('total_deductions', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('total_net_salary', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('status', sa.String(20), nullable=False, server_default='DRAFT'),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('processed_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('pdf_filename', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True)
    )
    
    # Now alter the status column to use the enum type
    conn.execute(sa.text("ALTER TABLE payrolls ALTER COLUMN status DROP DEFAULT"))
    conn.execute(sa.text("ALTER TABLE payrolls ALTER COLUMN status TYPE payrollstatus USING status::payrollstatus"))
    conn.execute(sa.text("ALTER TABLE payrolls ALTER COLUMN status SET DEFAULT 'DRAFT'::payrollstatus"))
    
    # Create payroll_entries table
    op.create_table(
        'payroll_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('payroll_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payrolls.id'), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('employee_number', sa.String(50), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('position', sa.String(200), nullable=True),
        sa.Column('department', sa.String(200), nullable=True),
        sa.Column('basic_salary', sa.Numeric(12, 2), nullable=False),
        sa.Column('allowances', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('gross_salary', sa.Numeric(12, 2), nullable=False),
        sa.Column('deductions', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('net_salary', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True)
    )
    
    # Create payroll_approvals table
    op.create_table(
        'payroll_approvals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('payroll_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payrolls.id'), nullable=False),
        sa.Column('approver_role', sa.String(50), nullable=False),
        sa.Column('approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('approved', sa.String(10), nullable=False),
        sa.Column('decision_date', sa.DateTime(), nullable=True),
        sa.Column('comments', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True)
    )
    
    # Create indexes
    op.create_index('idx_payrolls_period', 'payrolls', ['year', 'month'])
    op.create_index('idx_payrolls_status', 'payrolls', ['status', 'is_deleted'])
    op.create_index('idx_payrolls_created_by', 'payrolls', ['created_by_id'])
    op.create_index('idx_payroll_entries_payroll', 'payroll_entries', ['payroll_id'])
    op.create_index('idx_payroll_entries_employee', 'payroll_entries', ['employee_id'])
    op.create_index('idx_payroll_approvals_payroll', 'payroll_approvals', ['payroll_id'])
    op.create_index('idx_payroll_approvals_approver', 'payroll_approvals', ['approver_id'])
    op.create_index('idx_payroll_approvals_role', 'payroll_approvals', ['approver_role', 'approved'])


def downgrade():
    """Remove payroll tables"""
    
    # Drop indexes
    op.drop_index('idx_payroll_approvals_role', 'payroll_approvals')
    op.drop_index('idx_payroll_approvals_approver', 'payroll_approvals')
    op.drop_index('idx_payroll_approvals_payroll', 'payroll_approvals')
    op.drop_index('idx_payroll_entries_employee', 'payroll_entries')
    op.drop_index('idx_payroll_entries_payroll', 'payroll_entries')
    op.drop_index('idx_payrolls_created_by', 'payrolls')
    op.drop_index('idx_payrolls_status', 'payrolls')
    op.drop_index('idx_payrolls_period', 'payrolls')
    
    # Drop tables
    op.drop_table('payroll_approvals')
    op.drop_table('payroll_entries')
    op.drop_table('payrolls')
    
    # Drop enum
    sa.Enum(name='payrollstatus').drop(op.get_bind(), checkfirst=True)
