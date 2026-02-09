"""Add additional employee fields: blood type, work type, medical conditions, second emergency contact

Revision ID: 018_add_employee_additional_fields
Revises: 017_add_user_id_index
Create Date: 2026-01-04 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '018_add_employee_additional_fields'
down_revision = '017_add_user_id_index'
branch_labels = None
depends_on = None


def upgrade():
    # Create work_type enum
    worktype_enum = postgresql.ENUM('on_site', 'remote', 'hybrid', name='worktype', create_type=True)
    worktype_enum.create(op.get_bind(), checkfirst=True)
    
    # Add new columns to employees table
    op.add_column('employees', sa.Column('blood_type', sa.String(10), nullable=True))
    op.add_column('employees', sa.Column('medical_conditions', sa.Text(), nullable=True))
    op.add_column('employees', sa.Column('emergency_contact_2_name', sa.String(200), nullable=True))
    op.add_column('employees', sa.Column('emergency_contact_2_phone', sa.String(20), nullable=True))
    op.add_column('employees', sa.Column('emergency_contact_2_relationship', sa.String(100), nullable=True))
    op.add_column('employees', sa.Column('emergency_contact_2_note', sa.Text(), nullable=True))
    op.add_column('employees', sa.Column('work_type', postgresql.ENUM('on_site', 'remote', 'hybrid', name='worktype', create_type=False), nullable=True))


def downgrade():
    # Remove columns
    op.drop_column('employees', 'work_type')
    op.drop_column('employees', 'emergency_contact_2_note')
    op.drop_column('employees', 'emergency_contact_2_relationship')
    op.drop_column('employees', 'emergency_contact_2_phone')
    op.drop_column('employees', 'emergency_contact_2_name')
    op.drop_column('employees', 'medical_conditions')
    op.drop_column('employees', 'blood_type')
    
    # Drop enum type
    worktype_enum = postgresql.ENUM(name='worktype', create_type=False)
    worktype_enum.drop(op.get_bind(), checkfirst=True)
