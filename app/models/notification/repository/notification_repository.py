import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from models.notification.entity.notification_entity import NotificationEntity
from models.notification.entity.notification_model import Notification
from models.notification.mapper.notification_mapper import NotificationMapper
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class NotificationRepository:
    """Repository for Notification CRUD operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, domain: Notification) -> Notification:
        try:
            entity = NotificationMapper.to_entity(domain)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return NotificationMapper.to_domain(entity)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating Notification: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Notification]:
        try:
            stmt = select(NotificationEntity).where(
                NotificationEntity.id == record_id,
                NotificationEntity.is_deleted == False
            )
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(
                    f"Notification with id {record_id} not found",
                    ErrorType.NOT_FOUND
                )
            return NotificationMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error fetching Notification {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Notification]:
        try:
            stmt = select(NotificationEntity).where(NotificationEntity.is_deleted == False).offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            return NotificationMapper.to_domain_list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error fetching Notification list: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def update(self, record_id: int, updates: dict) -> Notification:
        try:
            await self.get_by_id(record_id)
            stmt = select(NotificationEntity).where(NotificationEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"Notification {record_id} not found", ErrorType.NOT_FOUND)
            updates["updated_at"] = datetime.now()
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            await self.session.commit()
            await self.session.refresh(entity)
            return NotificationMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating Notification {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        try:
            stmt = select(NotificationEntity).where(NotificationEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"Notification {record_id} not found", ErrorType.NOT_FOUND)
            # Soft delete
            entity.is_deleted = True
            entity.deleted_at = datetime.now()
            entity.deleted_by = deleted_by
            await self.session.commit()
            return True
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting Notification {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)
