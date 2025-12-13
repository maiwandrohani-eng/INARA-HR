"""Add performance indexes

Revision ID: 006
Revises: 005
Create Date: 2025-12-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for frequently queried columns"""
    
    # Helper function to create index if not exists
    def create_index_safe(index_name, table_name, columns):
        conn = op.get_bind()
        conn.execute(sa.text(f"""
            CREATE INDEX IF NOT EXISTS {index_name} 
            ON {table_name} ({', '.join(columns)})
        """))
    
    # Employees table indexes
    create_index_safe('idx_employees_work_email', 'employees', ['work_email'])
    create_index_safe('idx_employees_status', 'employees', ['status', 'is_deleted'])
    create_index_safe('idx_employees_department', 'employees', ['department_id'])
    create_index_safe('idx_employees_manager', 'employees', ['manager_id'])
    create_index_safe('idx_employees_hire_date', 'employees', ['hire_date'])
    
    # Approval requests indexes
    create_index_safe('idx_approval_requests_employee', 'approval_requests', ['employee_id', 'status'])
    create_index_safe('idx_approval_requests_approver', 'approval_requests', ['approver_id', 'status'])
    create_index_safe('idx_approval_requests_type', 'approval_requests', ['request_type', 'status'])
    create_index_safe('idx_approval_requests_submitted', 'approval_requests', ['submitted_at'])
    
    # Performance review cycles indexes (360 reviews)
    create_index_safe('idx_review_cycles_employee', 'performance_review_cycles', ['employee_id'])
    create_index_safe('idx_review_cycles_status', 'performance_review_cycles', ['status', 'created_at'])
    create_index_safe('idx_review_cycles_period', 'performance_review_cycles', ['review_period_start', 'review_period_end'])
    
    # Performance evaluations indexes
    create_index_safe('idx_evaluations_cycle', 'performance_evaluations', ['review_cycle_id'])
    create_index_safe('idx_evaluations_evaluator', 'performance_evaluations', ['evaluator_id'])
    create_index_safe('idx_evaluations_type', 'performance_evaluations', ['evaluator_type', 'status'])
    
    # Employment contracts indexes
    create_index_safe('idx_employment_contracts_employee', 'employment_contracts', ['employee_id'])
    create_index_safe('idx_employment_contracts_status', 'employment_contracts', ['status'])
    create_index_safe('idx_employment_contracts_dates', 'employment_contracts', ['start_date', 'end_date'])
    create_index_safe('idx_employment_contracts_country', 'employment_contracts', ['country_code', 'status'])
    
    # Contract extensions indexes
    create_index_safe('idx_extensions_contract', 'contract_extensions', ['contract_id'])
    create_index_safe('idx_extensions_employee', 'contract_extensions', ['employee_id'])
    create_index_safe('idx_extensions_status', 'contract_extensions', ['status'])
    
    # Resignations indexes
    create_index_safe('idx_resignations_employee', 'resignations', ['employee_id'])
    create_index_safe('idx_resignations_status', 'resignations', ['status'])
    create_index_safe('idx_resignations_date', 'resignations', ['resignation_date'])
    
    # Users table indexes
    create_index_safe('idx_users_is_active', 'users', ['is_active', 'is_deleted'])
    
    # User roles indexes
    create_index_safe('idx_user_roles_user', 'user_roles', ['user_id'])
    create_index_safe('idx_user_roles_role', 'user_roles', ['role_id'])


def downgrade():
    """Remove performance indexes"""
    
    # Drop all indexes in reverse order
    op.drop_index('idx_user_roles_role', 'user_roles')
    op.drop_index('idx_user_roles_user', 'user_roles')
    op.drop_index('idx_users_is_active', 'users')
    
    op.drop_index('idx_resignations_date', 'resignations')
    op.drop_index('idx_resignations_status', 'resignations')
    op.drop_index('idx_resignations_employee', 'resignations')
    
    op.drop_index('idx_extensions_status', 'contract_extensions')
    op.drop_index('idx_extensions_employee', 'contract_extensions')
    op.drop_index('idx_extensions_contract', 'contract_extensions')
    
    op.drop_index('idx_employment_contracts_country', 'employment_contracts')
    op.drop_index('idx_employment_contracts_dates', 'employment_contracts')
    op.drop_index('idx_employment_contracts_status', 'employment_contracts')
    op.drop_index('idx_employment_contracts_employee', 'employment_contracts')
    
    op.drop_index('idx_evaluations_type', 'performance_evaluations')
    op.drop_index('idx_evaluations_evaluator', 'performance_evaluations')
    op.drop_index('idx_evaluations_cycle', 'performance_evaluations')
    
    op.drop_index('idx_review_cycles_period', 'performance_review_cycles')
    op.drop_index('idx_review_cycles_status', 'performance_review_cycles')
    op.drop_index('idx_review_cycles_employee', 'performance_review_cycles')
    
    op.drop_index('idx_approval_requests_submitted', 'approval_requests')
    op.drop_index('idx_approval_requests_type', 'approval_requests')
    op.drop_index('idx_approval_requests_approver', 'approval_requests')
    op.drop_index('idx_approval_requests_employee', 'approval_requests')
    
    op.drop_index('idx_employees_hire_date', 'employees')
    op.drop_index('idx_employees_manager', 'employees')
    op.drop_index('idx_employees_department', 'employees')
    op.drop_index('idx_employees_status', 'employees')
    op.drop_index('idx_employees_work_email', 'employees')
