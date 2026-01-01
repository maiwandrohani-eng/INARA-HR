"""Notification System - Schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


# Notification Schemas
class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str
    category: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[uuid.UUID] = None
    action_url: Optional[str] = None
    priority: str = "normal"


class NotificationCreate(NotificationBase):
    user_id: uuid.UUID


class NotificationResponse(NotificationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Announcement Schemas
class AnnouncementBase(BaseModel):
    title: str
    content: str
    announcement_type: str
    target_audience: str = "all"
    target_department_id: Optional[uuid.UUID] = None
    target_role: Optional[str] = None
    expires_at: Optional[datetime] = None
    priority: str = "normal"


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementResponse(AnnouncementBase):
    id: uuid.UUID
    is_published: bool
    published_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

