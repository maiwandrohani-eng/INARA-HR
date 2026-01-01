"""Notification System - Repositories"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime
import uuid

from modules.notifications.models import Notification, Announcement
from modules.notifications.schemas import NotificationCreate, AnnouncementCreate


class NotificationRepository:
    """Repository for notification operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, notification_data: NotificationCreate, country_code: str) -> Notification:
        """Create a new notification"""
        notification_dict = notification_data.model_dump()
        notification_dict["country_code"] = country_code
        notification = Notification(**notification_dict)
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification
    
    async def get_user_notifications(
        self, 
        user_id: uuid.UUID, 
        is_read: Optional[bool] = None,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user"""
        query = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_deleted == False,
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > datetime.utcnow()
                )
            )
        )
        
        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
        
        query = query.order_by(Notification.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def mark_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Mark notification as read"""
        result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id,
                    Notification.is_deleted == False
                )
            )
        )
        notification = result.scalar_one_or_none()
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            await self.db.flush()
            return True
        return False
    
    async def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        """Mark all notifications as read for a user"""
        result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                    Notification.is_deleted == False
                )
            )
        )
        notifications = result.scalars().all()
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            count += 1
        await self.db.flush()
        return count
    
    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        """Get count of unread notifications"""
        result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                    Notification.is_deleted == False,
                    or_(
                        Notification.expires_at.is_(None),
                        Notification.expires_at > datetime.utcnow()
                    )
                )
            )
        )
        return len(list(result.scalars().all()))


class AnnouncementRepository:
    """Repository for announcement operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, announcement_data: AnnouncementCreate, created_by: uuid.UUID, country_code: str) -> Announcement:
        """Create a new announcement"""
        announcement_dict = announcement_data.model_dump()
        announcement_dict["created_by"] = created_by
        announcement_dict["country_code"] = country_code
        announcement = Announcement(**announcement_dict)
        self.db.add(announcement)
        await self.db.flush()
        await self.db.refresh(announcement)
        return announcement
    
    async def get_active_announcements(
        self, 
        department_id: Optional[uuid.UUID] = None,
        role: Optional[str] = None
    ) -> List[Announcement]:
        """Get active announcements"""
        query = select(Announcement).where(
            and_(
                Announcement.is_published == True,
                Announcement.is_deleted == False,
                or_(
                    Announcement.expires_at.is_(None),
                    Announcement.expires_at > datetime.utcnow()
                )
            )
        )
        
        # Filter by target audience
        conditions = []
        conditions.append(Announcement.target_audience == "all")
        
        if department_id:
            conditions.append(
                and_(
                    Announcement.target_audience == "department",
                    Announcement.target_department_id == department_id
                )
            )
        
        if role:
            conditions.append(
                and_(
                    Announcement.target_audience == "role",
                    Announcement.target_role == role
                )
            )
        
        if conditions:
            query = query.where(or_(*conditions))
        
        query = query.order_by(Announcement.published_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self) -> List[Announcement]:
        """Get all announcements"""
        query = select(Announcement).where(
            Announcement.is_deleted == False
        ).order_by(Announcement.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

