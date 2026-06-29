import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.notification.entity.notification_model import Notification
from models.notification.entity.notification_entity import NotificationEntity
from models.notification.mapper.notification_mapper import NotificationMapper
from models.notification.repository.notification_repository import NotificationRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class NotificationService:
    """Service layer for Notification business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(NotificationEntity, Notification, NotificationMapper)

    async def create(self, domain: Notification) -> Notification:
        """Create a new Notification"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating Notification: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Notification]:
        """Get Notification by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Notification]:
        """Get all Notification records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> Notification:
        """Update Notification"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete Notification"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
