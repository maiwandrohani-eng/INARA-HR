"""
Alembic Migration: Add 360-degree performance review tables

Revision ID: 004
Revises: 003
Create Date: 2024
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create performance_review_cycles table
    op.create_table(
        'performance_review_cycles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('review_period_start', sa.Date(), nullable=False),
        sa.Column('review_period_end', sa.Date(), nullable=False),
        sa.Column('review_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='in_progress'),
        sa.Column('final_rating', sa.Integer(), nullable=True),
        sa.Column('final_strengths', sa.Text(), nullable=True),
        sa.Column('final_areas_for_improvement', sa.Text(), nullable=True),
        sa.Column('final_development_plan', sa.Text(), nullable=True),
        sa.Column('employee_comments', sa.Text(), nullable=True),
        sa.Column('acknowledged_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Create indexes for performance_review_cycles
    op.create_index('ix_review_cycles_employee_id', 'performance_review_cycles', ['employee_id'])
    op.create_index('ix_review_cycles_status', 'performance_review_cycles', ['status'])
    
    # Create performance_evaluations table
    op.create_table(
        'performance_evaluations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('review_cycle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('performance_review_cycles.id'), nullable=False),
        sa.Column('evaluator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('evaluator_type', sa.String(20), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('strengths', sa.Text(), nullable=True),
        sa.Column('areas_for_improvement', sa.Text(), nullable=True),
        sa.Column('achievements', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('technical_skills', sa.Integer(), nullable=True),
        sa.Column('communication', sa.Integer(), nullable=True),
        sa.Column('teamwork', sa.Integer(), nullable=True),
        sa.Column('leadership', sa.Integer(), nullable=True),
        sa.Column('problem_solving', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('submitted_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )
    
    # Create indexes for performance_evaluations
    op.create_index('ix_evaluations_review_cycle_id', 'performance_evaluations', ['review_cycle_id'])
    op.create_index('ix_evaluations_evaluator_id', 'performance_evaluations', ['evaluator_id'])
    op.create_index('ix_evaluations_status', 'performance_evaluations', ['status'])
    op.create_index('ix_evaluations_type', 'performance_evaluations', ['evaluator_type'])


def downgrade():
    # Drop performance_evaluations table
    op.drop_index('ix_evaluations_type', table_name='performance_evaluations')
    op.drop_index('ix_evaluations_status', table_name='performance_evaluations')
    op.drop_index('ix_evaluations_evaluator_id', table_name='performance_evaluations')
    op.drop_index('ix_evaluations_review_cycle_id', table_name='performance_evaluations')
    op.drop_table('performance_evaluations')
    
    # Drop performance_review_cycles table
    op.drop_index('ix_review_cycles_status', table_name='performance_review_cycles')
    op.drop_index('ix_review_cycles_employee_id', table_name='performance_review_cycles')
    op.drop_table('performance_review_cycles')
