"""Notification System - Routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from core.database import get_db
from core.dependencies import get_current_active_user
from modules.notifications.services import NotificationService
from modules.notifications.schemas import NotificationCreate, AnnouncementCreate

router = APIRouter()


@router.get("/notifications")
async def get_my_notifications(
    is_read: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get current user's notifications"""
    notification_service = NotificationService(db)
    notifications = await notification_service.get_user_notifications(
        uuid.UUID(current_user["id"]), 
        is_read=is_read
    )
    return notifications


@router.get("/notifications/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get unread notification count"""
    notification_service = NotificationService(db)
    count = await notification_service.get_unread_count(uuid.UUID(current_user["id"]))
    return count


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Mark notification as read"""
    try:
        notification_uuid = uuid.UUID(notification_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid notification ID format")
    
    notification_service = NotificationService(db)
    result = await notification_service.mark_as_read(notification_uuid, uuid.UUID(current_user["id"]))
    return result


@router.post("/announcements", status_code=201)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new announcement (admin only)"""
    notification_service = NotificationService(db)
    announcement = await notification_service.create_announcement(
        announcement_data,
        uuid.UUID(current_user["id"])
    )
    return announcement


@router.get("/announcements")
async def get_announcements(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all active announcements"""
    notification_service = NotificationService(db)
    announcements = await notification_service.get_announcements()
    return announcements

