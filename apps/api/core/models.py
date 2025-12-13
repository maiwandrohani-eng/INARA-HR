"""
Base Models
Common database model mixins and base classes
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid


class UUIDMixin:
    """Mixin to add UUID primary key"""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """Mixin to add soft delete functionality"""
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)


class AuditMixin:
    """Mixin to track who created/updated records"""
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)


class TenantMixin:
    """Mixin for multi-tenant support (country-level)"""
    country_code = Column(String(2), index=True, nullable=True)  # ISO 3166-1 alpha-2


class NoteMixin:
    """Mixin to add notes field"""
    notes = Column(Text, nullable=True)


# Common base class combining frequently used mixins
class BaseModel(UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Base model with:
    - UUID primary key
    - Created/updated timestamps
    - Soft delete support
    """
    pass
