"""
Employee Personal Files Migration
Creates tables for employee documents, contracts, extensions, and resignations

Revision ID: 005
Revises: 004
Create Date: 2024-01-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from uuid import uuid4


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    from sqlalchemy.dialects import postgresql
    
    # Define enums (they will be automatically created when the table is created)
    document_category = postgresql.ENUM(
        'CONTRACT', 'CONTRACT_EXTENSION', 'EDUCATIONAL', 'REFERENCE_CHECK',
        'INTERVIEW_RECORD', 'BACKGROUND_CHECK', 'ID_DOCUMENT', 'BANK_DETAILS',
        'EMERGENCY_CONTACT', 'RESIGNATION', 'TERMINATION', 'PERFORMANCE_REVIEW',
        'DISCIPLINARY', 'TRAINING_CERTIFICATE', 'OTHER',
        name='documentcategory',
        create_type=True
    )
    
    contract_status = postgresql.ENUM(
        'DRAFT', 'ACTIVE', 'EXTENDED', 'EXPIRED', 'TERMINATED',
        name='contractstatus',
        create_type=True
    )
    
    extension_status = postgresql.ENUM(
        'PENDING', 'ACCEPTED', 'REJECTED', 'EXPIRED',
        name='extensionstatus',
        create_type=True
    )
    
    resignation_status = postgresql.ENUM(
        'SUBMITTED', 'ACCEPTED_BY_SUPERVISOR', 'ACCEPTED_BY_HR',
        'ACCEPTED_BY_CEO', 'COMPLETED', 'WITHDRAWN',
        name='resignationstatus',
        create_type=True
    )
    
    # Create personal_file_documents table
    op.create_table(
        'personal_file_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('category', document_category, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_size', sa.BigInteger, nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('uploaded_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('is_confidential', sa.Boolean, default=False, nullable=False),
        sa.Column('expiry_date', sa.Date, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
        
        # Multi-tenancy
        sa.Column('country_code', sa.String(3), nullable=False, default='AFG'),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Create indexes for personal_file_documents
    op.create_index('idx_personal_file_documents_employee_id', 'personal_file_documents', ['employee_id'])
    op.create_index('idx_personal_file_documents_category', 'personal_file_documents', ['category'])
    op.create_index('idx_personal_file_documents_uploaded_at', 'personal_file_documents', ['uploaded_at'])
    
    # Create employment_contracts table
    op.create_table(
        'employment_contracts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('contract_number', sa.String(100), unique=True, nullable=False),
        sa.Column('position_title', sa.String(200), nullable=False),
        sa.Column('location', sa.String(200), nullable=False),
        sa.Column('contract_type', sa.String(100), nullable=False),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('signed_date', sa.Date, nullable=True),
        sa.Column('monthly_salary', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, default='USD'),
        
        # Performance reviews
        sa.Column('june_review_date', sa.Date, nullable=True),
        sa.Column('december_review_date', sa.Date, nullable=True),
        sa.Column('june_review_outcome', sa.Text, nullable=True),
        sa.Column('december_review_outcome', sa.Text, nullable=True),
        
        # Termination
        sa.Column('termination_date', sa.Date, nullable=True),
        sa.Column('termination_reason', sa.Text, nullable=True),
        sa.Column('notice_period_days', sa.Integer, nullable=False, default=30),
        
        # Status
        sa.Column('status', contract_status, nullable=False, default='DRAFT'),
        
        # Document reference
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('personal_file_documents.id'), nullable=True),
        
        # Multi-tenancy
        sa.Column('country_code', sa.String(3), nullable=False, default='AFG'),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Create indexes for employment_contracts
    op.create_index('idx_employment_contracts_employee_id', 'employment_contracts', ['employee_id'])
    op.create_index('idx_employment_contracts_status', 'employment_contracts', ['status'])
    op.create_index('idx_employment_contracts_start_date', 'employment_contracts', ['start_date'])
    op.create_index('idx_employment_contracts_end_date', 'employment_contracts', ['end_date'])
    
    # Create contract_extensions table
    op.create_table(
        'contract_extensions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('contract_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employment_contracts.id'), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('extension_number', sa.Integer, nullable=False),
        
        # New terms
        sa.Column('new_start_date', sa.Date, nullable=False),
        sa.Column('new_end_date', sa.Date, nullable=False),
        sa.Column('new_monthly_salary', sa.Numeric(12, 2), nullable=True),
        sa.Column('salary_change_reason', sa.Text, nullable=True),
        sa.Column('new_position_title', sa.String(200), nullable=True),
        sa.Column('new_location', sa.String(200), nullable=True),
        sa.Column('terms_changes', sa.Text, nullable=True),
        
        # Digital signature
        sa.Column('employee_accepted_at', sa.DateTime, nullable=True),
        sa.Column('employee_signature_ip', sa.String(45), nullable=True),
        
        # Notifications
        sa.Column('notified_at', sa.DateTime, nullable=True),
        sa.Column('reminder_sent_at', sa.DateTime, nullable=True),
        sa.Column('expires_at', sa.Date, nullable=True),
        
        # Status
        sa.Column('status', extension_status, nullable=False, default='PENDING'),
        
        # Document reference
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('personal_file_documents.id'), nullable=True),
        
        # Multi-tenancy
        sa.Column('country_code', sa.String(3), nullable=False, default='AFG'),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Create indexes for contract_extensions
    op.create_index('idx_contract_extensions_contract_id', 'contract_extensions', ['contract_id'])
    op.create_index('idx_contract_extensions_employee_id', 'contract_extensions', ['employee_id'])
    op.create_index('idx_contract_extensions_status', 'contract_extensions', ['status'])
    op.create_index('idx_contract_extensions_expires_at', 'contract_extensions', ['expires_at'])
    
    # Create resignations table
    op.create_table(
        'resignations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('resignation_number', sa.String(100), unique=True, nullable=False),
        sa.Column('resignation_date', sa.Date, nullable=False),
        sa.Column('intended_last_working_day', sa.Date, nullable=False),
        sa.Column('reason', sa.Text, nullable=False),
        sa.Column('notice_period_days', sa.Integer, nullable=False, default=30),
        
        # Supervisor approval
        sa.Column('supervisor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=True),
        sa.Column('supervisor_accepted_at', sa.DateTime, nullable=True),
        sa.Column('supervisor_comments', sa.Text, nullable=True),
        
        # HR approval
        sa.Column('hr_accepted_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('hr_accepted_at', sa.DateTime, nullable=True),
        sa.Column('hr_comments', sa.Text, nullable=True),
        
        # CEO approval
        sa.Column('ceo_accepted_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('ceo_accepted_at', sa.DateTime, nullable=True),
        sa.Column('ceo_comments', sa.Text, nullable=True),
        sa.Column('approved_last_working_day', sa.Date, nullable=True),
        
        # Exit interview
        sa.Column('exit_interview_completed', sa.Boolean, default=False, nullable=False),
        sa.Column('exit_interview_date', sa.Date, nullable=True),
        
        # Status
        sa.Column('status', resignation_status, nullable=False, default='SUBMITTED'),
        
        # Document reference
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('personal_file_documents.id'), nullable=True),
        
        # Multi-tenancy
        sa.Column('country_code', sa.String(3), nullable=False, default='AFG'),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create indexes for resignations
    op.create_index('idx_resignations_employee_id', 'resignations', ['employee_id'])
    op.create_index('idx_resignations_supervisor_id', 'resignations', ['supervisor_id'])
    op.create_index('idx_resignations_status', 'resignations', ['status'])
    op.create_index('idx_resignations_resignation_date', 'resignations', ['resignation_date'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('resignations')
    op.drop_table('contract_extensions')
    op.drop_table('employment_contracts')
    op.drop_table('personal_file_documents')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS resignationstatus')
    op.execute('DROP TYPE IF EXISTS extensionstatus')
    op.execute('DROP TYPE IF EXISTS contractstatus')
    op.execute('DROP TYPE IF EXISTS documentcategory')
