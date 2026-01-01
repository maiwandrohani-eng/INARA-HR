"""
In-app Notification System - Models
Notifications, announcements, messaging
"""

from sqlalchemy import Column, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from core.database import Base
from core.models import BaseModel, TenantMixin


class Notification(BaseModel, TenantMixin, Base):
    """In-app notifications for users"""
    __tablename__ = "notifications"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Notification details
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # info, warning, success, error, approval, system
    category = Column(String(50), nullable=True)  # leave, timesheet, performance, etc.
    
    # Reference to related entity
    related_entity_type = Column(String(50), nullable=True)  # leave_request, timesheet, etc.
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    
    # Action link
    action_url = Column(String(500), nullable=True)
    
    # Priority
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="notifications")
    
    def __repr__(self):
        return f"<Notification {self.title} - {self.user_id}>"


class Announcement(BaseModel, TenantMixin, Base):
    """Company/department-wide announcements"""
    __tablename__ = "announcements"
    
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Announcement details
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    announcement_type = Column(String(50), nullable=False)  # company, department, general
    
    # Targeting
    target_audience = Column(String(50), default="all")  # all, department, role, specific_users
    target_department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=True)
    target_role = Column(String(50), nullable=True)
    
    # Visibility
    is_published = Column(Boolean, default=False, nullable=False)
    published_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Priority
    priority = Column(String(20), default="normal")
    
    # Relationships
    department = relationship("Department", backref="announcements")
    
    def __repr__(self):
        return f"<Announcement {self.title}>"

