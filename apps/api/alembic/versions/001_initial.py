"""Initial migration - Create all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create all tables for INARA HRIS
    
    This migration creates all tables defined in the models.
    Run: alembic upgrade head
    """
    # Tables will be created automatically from models
    # when running: alembic revision --autogenerate -m "message"
    pass


def downgrade() -> None:
    """Drop all tables"""
    pass
