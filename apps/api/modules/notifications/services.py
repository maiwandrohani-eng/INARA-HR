"""Notification System - Services"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from modules.notifications.repositories import NotificationRepository, AnnouncementRepository
from modules.notifications.schemas import NotificationCreate, AnnouncementCreate
from core.exceptions import NotFoundException


class NotificationService:
    """Service for notification operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_repo = NotificationRepository(db)
        self.announcement_repo = AnnouncementRepository(db)
    
    async def create_notification(
        self, 
        user_id: uuid.UUID, 
        title: str, 
        message: str, 
        notification_type: str = "info",
        category: Optional[str] = None,
        action_url: Optional[str] = None,
        country_code: str = "US"
    ) -> dict:
        """Create and send a notification"""
        notification_data = NotificationCreate(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
            action_url=action_url
        )
        notification = await self.notification_repo.create(notification_data, country_code)
        await self.db.commit()
        return {
            "id": str(notification.id),
            "title": notification.title,
            "is_read": notification.is_read
        }
    
    async def get_user_notifications(
        self, 
        user_id: uuid.UUID, 
        is_read: Optional[bool] = None
    ) -> List[dict]:
        """Get notifications for a user"""
        notifications = await self.notification_repo.get_user_notifications(user_id, is_read=is_read)
        return [{
            "id": str(n.id),
            "title": n.title,
            "message": n.message,
            "notification_type": n.notification_type,
            "category": n.category,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "action_url": n.action_url
        } for n in notifications]
    
    async def mark_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """Mark notification as read"""
        success = await self.notification_repo.mark_as_read(notification_id, user_id)
        if not success:
            raise NotFoundException(resource="Notification")
        
        await self.db.commit()
        return {"success": True}
    
    async def get_unread_count(self, user_id: uuid.UUID) -> dict:
        """Get count of unread notifications"""
        count = await self.notification_repo.get_unread_count(user_id)
        return {"unread_count": count}
    
    async def create_announcement(
        self, 
        announcement_data: AnnouncementCreate, 
        created_by: uuid.UUID,
        country_code: str = "US"
    ) -> dict:
        """Create a new announcement"""
        announcement = await self.announcement_repo.create(announcement_data, created_by, country_code)
        await self.db.commit()
        return {
            "id": str(announcement.id),
            "title": announcement.title,
            "is_published": announcement.is_published
        }
    
    async def get_announcements(self) -> List[dict]:
        """Get all announcements"""
        announcements = await self.announcement_repo.get_all()
        return [{
            "id": str(a.id),
            "title": a.title,
            "content": a.content,
            "announcement_type": a.announcement_type,
            "target_audience": a.target_audience,
            "priority": a.priority,
            "is_published": a.is_published,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "expires_at": a.expires_at.isoformat() if a.expires_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        } for a in announcements]

