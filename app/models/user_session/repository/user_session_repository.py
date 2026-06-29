import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from models.user_session.entity.user_session_entity import UserSessionEntity
from models.user_session.entity.user_session_model import UserSession
from models.user_session.mapper.user_session_mapper import UserSessionMapper
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class UserSessionRepository:
    """Repository for UserSession CRUD operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, domain: UserSession) -> UserSession:
        try:
            entity = UserSessionMapper.to_entity(domain)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return UserSessionMapper.to_domain(entity)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating UserSession: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[UserSession]:
        try:
            stmt = select(UserSessionEntity).where(
                UserSessionEntity.id == record_id,
                UserSessionEntity.is_deleted == False
            )
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(
                    f"UserSession with id {record_id} not found",
                    ErrorType.NOT_FOUND
                )
            return UserSessionMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error fetching UserSession {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserSession]:
        try:
            stmt = select(UserSessionEntity).where(UserSessionEntity.is_deleted == False).offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            return UserSessionMapper.to_domain_list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error fetching UserSession list: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def update(self, record_id: int, updates: dict) -> UserSession:
        try:
            await self.get_by_id(record_id)
            stmt = select(UserSessionEntity).where(UserSessionEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"UserSession {record_id} not found", ErrorType.NOT_FOUND)
            updates["updated_at"] = datetime.now()
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            await self.session.commit()
            await self.session.refresh(entity)
            return UserSessionMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating UserSession {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        try:
            stmt = select(UserSessionEntity).where(UserSessionEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"UserSession {record_id} not found", ErrorType.NOT_FOUND)
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
            logger.error(f"Error deleting UserSession {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)
