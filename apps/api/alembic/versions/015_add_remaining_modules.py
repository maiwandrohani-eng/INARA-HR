"""add succession, engagement, workforce, and exit management modules

Revision ID: 015
Revises: 014
Create Date: 2025-12-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade():
    # ============= Succession Planning Tables =============
    op.create_table(
        'key_positions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('position_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('criticality_level', sa.String(length=20), nullable=False),
        sa.Column('business_impact', sa.Text(), nullable=True),
        sa.Column('vacancy_risk', sa.String(length=20), nullable=True),
        sa.Column('current_incumbent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('has_successor', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('succession_status', sa.String(length=20), nullable=True, server_default='not_planned'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ),
        sa.ForeignKeyConstraint(['current_incumbent_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'successors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key_position_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('successor_type', sa.String(length=20), nullable=False),
        sa.Column('readiness_level', sa.String(length=20), nullable=False),
        sa.Column('readiness_score', sa.Integer(), nullable=True),
        sa.Column('skills_gap_analysis', sa.Text(), nullable=True),
        sa.Column('development_needs', sa.Text(), nullable=True),
        sa.Column('development_plan_created', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('development_plan_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['key_position_id'], ['key_positions.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'succession_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key_position_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_name', sa.String(length=200), nullable=False),
        sa.Column('plan_date', sa.Date(), nullable=False),
        sa.Column('review_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='draft'),
        sa.Column('expected_transition_date', sa.Date(), nullable=True),
        sa.Column('risk_mitigation_strategies', sa.Text(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['key_position_id'], ['key_positions.id'], ),
        sa.ForeignKeyConstraint(['approved_by'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # ============= Employee Engagement Tables =============
    op.create_table(
        'surveys',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('survey_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_anonymous', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('target_audience', sa.String(length=50), nullable=True, server_default='all'),
        sa.Column('target_department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('response_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_rating', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['target_department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'survey_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('survey_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(length=50), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('options', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['survey_id'], ['surveys.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'survey_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('survey_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('submitted_date', sa.DateTime(), nullable=False),
        sa.Column('overall_rating', sa.Integer(), nullable=True),
        sa.Column('is_complete', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['survey_id'], ['surveys.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'survey_answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('response_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('answer_text', sa.Text(), nullable=True),
        sa.Column('answer_value', sa.String(length=200), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['response_id'], ['survey_responses.id'], ),
        sa.ForeignKeyConstraint(['question_id'], ['survey_questions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'recognitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recognized_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recognition_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('recognition_date', sa.Date(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['recognized_by_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # ============= Workforce Planning Tables =============
    op.create_table(
        'workforce_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_name', sa.String(length=200), nullable=False),
        sa.Column('plan_year', sa.Integer(), nullable=False),
        sa.Column('plan_start_date', sa.Date(), nullable=False),
        sa.Column('plan_end_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='draft'),
        sa.Column('total_budget', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'position_requisitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workforce_plan_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('position_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requisition_number', sa.String(length=100), nullable=False),
        sa.Column('job_title', sa.String(length=200), nullable=False),
        sa.Column('employment_type', sa.String(length=50), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('business_case', sa.Text(), nullable=True),
        sa.Column('budgeted_salary_min', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('budgeted_salary_max', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('requested_start_date', sa.Date(), nullable=True),
        sa.Column('urgency', sa.String(length=20), nullable=True, server_default='normal'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='draft'),
        sa.Column('requested_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_date', sa.Date(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['workforce_plan_id'], ['workforce_plans.id'], ),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['requested_by'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['approved_by'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('requisition_number')
    )

    op.create_table(
        'headcount_forecasts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workforce_plan_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('position_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('forecast_month', sa.Integer(), nullable=False),
        sa.Column('forecast_year', sa.Integer(), nullable=False),
        sa.Column('current_headcount', sa.Integer(), nullable=False),
        sa.Column('planned_headcount', sa.Integer(), nullable=False),
        sa.Column('budgeted_headcount', sa.Integer(), nullable=False),
        sa.Column('headcount_variance', sa.Integer(), nullable=True),
        sa.Column('cost_impact', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['workforce_plan_id'], ['workforce_plans.id'], ),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # ============= Exit Management Tables =============
    op.create_table(
        'exit_interviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resignation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conducted_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interview_date', sa.Date(), nullable=False),
        sa.Column('interview_type', sa.String(length=50), nullable=True, server_default='face_to_face'),
        sa.Column('q1_reason_for_leaving', sa.Text(), nullable=True),
        sa.Column('q2_overall_satisfaction', sa.Integer(), nullable=True),
        sa.Column('q3_management_rating', sa.Integer(), nullable=True),
        sa.Column('q4_work_environment_rating', sa.Integer(), nullable=True),
        sa.Column('q5_would_recommend', sa.Boolean(), nullable=True),
        sa.Column('q6_improvement_suggestions', sa.Text(), nullable=True),
        sa.Column('q7_positive_feedback', sa.Text(), nullable=True),
        sa.Column('q8_future_plans', sa.Text(), nullable=True),
        sa.Column('overall_feedback', sa.Text(), nullable=True),
        sa.Column('feedback_summary', sa.Text(), nullable=True),
        sa.Column('is_complete', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_confidential', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['resignation_id'], ['resignations.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['conducted_by_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'exit_checklists',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resignation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('checklist_item', sa.String(length=200), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('completed_date', sa.DateTime(), nullable=True),
        sa.Column('completed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('verification_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('verified_date', sa.DateTime(), nullable=True),
        sa.Column('is_critical', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['resignation_id'], ['resignations.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['assigned_to'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['completed_by'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['verified_by'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'knowledge_transfers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resignation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transferred_to_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('transfer_date', sa.Date(), nullable=True),
        sa.Column('knowledge_area', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('document_url', sa.String(length=500), nullable=True),
        sa.Column('resources', sa.Text(), nullable=True),
        sa.Column('is_complete', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('verified_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['resignation_id'], ['resignations.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['transferred_to_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['verified_by'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('knowledge_transfers')
    op.drop_table('exit_checklists')
    op.drop_table('exit_interviews')
    op.drop_table('headcount_forecasts')
    op.drop_table('position_requisitions')
    op.drop_table('workforce_plans')
    op.drop_table('recognitions')
    op.drop_table('survey_answers')
    op.drop_table('survey_responses')
    op.drop_table('survey_questions')
    op.drop_table('surveys')
    op.drop_table('succession_plans')
    op.drop_table('successors')
    op.drop_table('key_positions')

