import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from models.user_specialite.entity.user_specialite_entity import UserSpecialiteEntity
from models.user_specialite.entity.user_specialite_model import UserSpecialite
from models.user_specialite.mapper.user_specialite_mapper import UserSpecialiteMapper
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class UserSpecialiteRepository:
    """Repository for UserSpecialite CRUD operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, domain: UserSpecialite) -> UserSpecialite:
        try:
            entity = UserSpecialiteMapper.to_entity(domain)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return UserSpecialiteMapper.to_domain(entity)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating UserSpecialite: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[UserSpecialite]:
        try:
            stmt = select(UserSpecialiteEntity).where(
                UserSpecialiteEntity.id == record_id,
                UserSpecialiteEntity.is_deleted == False
            )
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(
                    f"UserSpecialite with id {record_id} not found",
                    ErrorType.NOT_FOUND
                )
            return UserSpecialiteMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error fetching UserSpecialite {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserSpecialite]:
        try:
            stmt = select(UserSpecialiteEntity).where(UserSpecialiteEntity.is_deleted == False).offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            return UserSpecialiteMapper.to_domain_list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error fetching UserSpecialite list: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def update(self, record_id: int, updates: dict) -> UserSpecialite:
        try:
            await self.get_by_id(record_id)
            stmt = select(UserSpecialiteEntity).where(UserSpecialiteEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"UserSpecialite {record_id} not found", ErrorType.NOT_FOUND)
            updates["updated_at"] = datetime.now()
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            await self.session.commit()
            await self.session.refresh(entity)
            return UserSpecialiteMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating UserSpecialite {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        try:
            stmt = select(UserSpecialiteEntity).where(UserSpecialiteEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"UserSpecialite {record_id} not found", ErrorType.NOT_FOUND)
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
            logger.error(f"Error deleting UserSpecialite {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)
