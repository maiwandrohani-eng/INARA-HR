"""add recruitment module tables

Revision ID: 011
Revises: 010
Create Date: 2025-12-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade():
    # Create job_postings table
    op.create_table(
        'job_postings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('position_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('responsibilities', sa.Text(), nullable=True),
        sa.Column('employment_type', sa.String(length=50), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('salary_range_min', sa.String(length=20), nullable=True),
        sa.Column('salary_range_max', sa.String(length=20), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='draft'),
        sa.Column('posted_date', sa.Date(), nullable=True),
        sa.Column('closing_date', sa.Date(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_job_postings_country_code', 'job_postings', ['country_code'])
    op.create_index('ix_job_postings_status', 'job_postings', ['status'])
    op.create_index('ix_job_postings_posted_date', 'job_postings', ['posted_date'])

    # Create applications table
    op.create_table(
        'applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_posting_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('resume_url', sa.String(length=500), nullable=True),
        sa.Column('cover_letter', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='received'),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('applied_date', sa.Date(), nullable=False),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['job_posting_id'], ['job_postings.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_applications_job_posting_id', 'applications', ['job_posting_id'])
    op.create_index('ix_applications_status', 'applications', ['status'])
    op.create_index('ix_applications_email', 'applications', ['email'])

    # Create interviews table
    op.create_table(
        'interviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interview_type', sa.String(length=50), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('interviewer_ids', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='scheduled'),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_interviews_application_id', 'interviews', ['application_id'])
    op.create_index('ix_interviews_status', 'interviews', ['status'])
    op.create_index('ix_interviews_scheduled_date', 'interviews', ['scheduled_date'])

    # Create offer_letters table
    op.create_table(
        'offer_letters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('position_title', sa.String(length=200), nullable=False),
        sa.Column('salary', sa.String(length=20), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('offer_letter_url', sa.String(length=500), nullable=True),
        sa.Column('sent_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='draft'),
        sa.Column('accepted_date', sa.Date(), nullable=True),
        sa.Column('rejected_reason', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_offer_letters_application_id', 'offer_letters', ['application_id'])
    op.create_index('ix_offer_letters_status', 'offer_letters', ['status'])


def downgrade():
    op.drop_index('ix_offer_letters_status', table_name='offer_letters')
    op.drop_index('ix_offer_letters_application_id', table_name='offer_letters')
    op.drop_table('offer_letters')
    
    op.drop_index('ix_interviews_scheduled_date', table_name='interviews')
    op.drop_index('ix_interviews_status', table_name='interviews')
    op.drop_index('ix_interviews_application_id', table_name='interviews')
    op.drop_table('interviews')
    
    op.drop_index('ix_applications_email', table_name='applications')
    op.drop_index('ix_applications_status', table_name='applications')
    op.drop_index('ix_applications_job_posting_id', table_name='applications')
    op.drop_table('applications')
    
    op.drop_index('ix_job_postings_posted_date', table_name='job_postings')
    op.drop_index('ix_job_postings_status', table_name='job_postings')
    op.drop_index('ix_job_postings_country_code', table_name='job_postings')
    op.drop_table('job_postings')

