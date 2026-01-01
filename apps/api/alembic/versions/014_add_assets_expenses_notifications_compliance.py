"""add assets, expenses, notifications, and compliance modules

Revision ID: 014
Revises: 013
Create Date: 2025-12-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade():
    # Create assets table
    op.create_table(
        'assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_number', sa.String(length=100), nullable=False),
        sa.Column('asset_name', sa.String(length=200), nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('manufacturer', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('purchase_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('current_value', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='available'),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('specifications', sa.Text(), nullable=True),
        sa.Column('warranty_start_date', sa.Date(), nullable=True),
        sa.Column('warranty_end_date', sa.Date(), nullable=True),
        sa.Column('warranty_provider', sa.String(length=200), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_number'),
        sa.UniqueConstraint('serial_number')
    )
    op.create_index('ix_assets_asset_type', 'assets', ['asset_type'])
    op.create_index('ix_assets_status', 'assets', ['status'])

    # Create asset_assignments table
    op.create_table(
        'asset_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_date', sa.Date(), nullable=False),
        sa.Column('expected_return_date', sa.Date(), nullable=True),
        sa.Column('actual_return_date', sa.Date(), nullable=True),
        sa.Column('assignment_type', sa.String(length=50), nullable=True, server_default='permanent'),
        sa.Column('condition_at_assignment', sa.String(length=50), nullable=True),
        sa.Column('condition_at_return', sa.String(length=50), nullable=True),
        sa.Column('assignment_notes', sa.Text(), nullable=True),
        sa.Column('return_notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='active'),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_asset_assignments_employee_id', 'asset_assignments', ['employee_id'])

    # Create asset_maintenance table
    op.create_table(
        'asset_maintenance',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('maintenance_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=True),
        sa.Column('completed_date', sa.Date(), nullable=True),
        sa.Column('vendor_name', sa.String(length=200), nullable=True),
        sa.Column('vendor_contact', sa.String(length=200), nullable=True),
        sa.Column('cost', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='scheduled'),
        sa.Column('result_notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create expense_reports table
    op.create_table(
        'expense_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_number', sa.String(length=100), nullable=False),
        sa.Column('report_date', sa.Date(), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=True),
        sa.Column('period_end', sa.Date(), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='draft'),
        sa.Column('approver_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_date', sa.Date(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('payment_date', sa.Date(), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_reference', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['approver_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('report_number')
    )
    op.create_index('ix_expense_reports_status', 'expense_reports', ['status'])

    # Create expense_items table
    op.create_table(
        'expense_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expense_report_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('expense_type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('exchange_rate', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('amount_in_report_currency', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('vendor_name', sa.String(length=200), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('receipt_url', sa.String(length=500), nullable=True),
        sa.Column('receipt_attached', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('business_purpose', sa.Text(), nullable=True),
        sa.Column('project_name', sa.String(length=200), nullable=True),
        sa.Column('client_name', sa.String(length=200), nullable=True),
        sa.Column('item_status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['expense_report_id'], ['expense_reports.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('related_entity_type', sa.String(length=50), nullable=True),
        sa.Column('related_entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('action_url', sa.String(length=500), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True, server_default='normal'),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])

    # Create announcements table
    op.create_table(
        'announcements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('announcement_type', sa.String(length=50), nullable=False),
        sa.Column('target_audience', sa.String(length=50), nullable=True, server_default='all'),
        sa.Column('target_department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('target_role', sa.String(length=50), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True, server_default='normal'),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['target_department_id'], ['departments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create policies table
    op.create_table(
        'policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('policy_type', sa.String(length=50), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('document_url', sa.String(length=500), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('requires_acknowledgment', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('applicable_to', sa.String(length=50), nullable=True, server_default='all'),
        sa.Column('applicable_department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('applicable_role', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['applicable_department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create policy_acknowledgments table
    op.create_table(
        'policy_acknowledgments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('acknowledged_date', sa.DateTime(), nullable=False),
        sa.Column('acknowledged_version', sa.String(length=20), nullable=False),
        sa.Column('is_acknowledged', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create compliance_trainings table
    op.create_table(
        'compliance_trainings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('training_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('duration_minutes', sa.String(length=20), nullable=True),
        sa.Column('training_url', sa.String(length=500), nullable=True),
        sa.Column('is_online', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('required_for', sa.String(length=50), nullable=True, server_default='all'),
        sa.Column('frequency', sa.String(length=50), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
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

    # Create training_completions table
    op.create_table(
        'training_completions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('compliance_training_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('completed_date', sa.DateTime(), nullable=False),
        sa.Column('expiration_date', sa.DateTime(), nullable=True),
        sa.Column('certificate_url', sa.String(length=500), nullable=True),
        sa.Column('score', sa.String(length=20), nullable=True),
        sa.Column('passed', sa.Boolean(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['compliance_training_id'], ['compliance_trainings.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('training_completions')
    op.drop_table('compliance_trainings')
    op.drop_table('policy_acknowledgments')
    op.drop_table('policies')
    op.drop_table('announcements')
    op.drop_index('ix_notifications_is_read', table_name='notifications')
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')
    op.drop_table('expense_items')
    op.drop_index('ix_expense_reports_status', table_name='expense_reports')
    op.drop_table('expense_reports')
    op.drop_table('asset_maintenance')
    op.drop_index('ix_asset_assignments_employee_id', table_name='asset_assignments')
    op.drop_table('asset_assignments')
    op.drop_index('ix_assets_status', table_name='assets')
    op.drop_index('ix_assets_asset_type', table_name='assets')
    op.drop_table('assets')

