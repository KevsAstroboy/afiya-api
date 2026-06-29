import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from models.user.entity.user_entity import UserEntity
from models.user.entity.user_model import User
from models.user.mapper.user_mapper import UserMapper
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for User CRUD operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, domain: User) -> User:
        try:
            entity = UserMapper.to_entity(domain)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return UserMapper.to_domain(entity)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating User: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def exists_by_phone_number(self, phone: str) -> bool:
        stmt = select(UserEntity.id).where(UserEntity.telephone == phone).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar() is not None

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(UserEntity.email).where(UserEntity.email == email).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar() is not None

    async def get_by_id(self, record_id: int) -> Optional[User]:
        try:
            stmt = select(UserEntity).where(
                UserEntity.id == record_id,
                UserEntity.is_deleted == False
            )
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(
                    f"User with id {record_id} not found",
                    ErrorType.NOT_FOUND
                )
            return UserMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error fetching User {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        try:
            stmt = select(UserEntity).where(UserEntity.is_deleted == False).offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            return UserMapper.to_domain_list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error fetching User list: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def update(self, record_id: int, updates: dict) -> User:
        try:
            await self.get_by_id(record_id)
            stmt = select(UserEntity).where(UserEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"User {record_id} not found", ErrorType.NOT_FOUND)
            updates["updated_at"] = datetime.now()
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            await self.session.commit()
            await self.session.refresh(entity)
            return UserMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating User {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        try:
            stmt = select(UserEntity).where(UserEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"User {record_id} not found", ErrorType.NOT_FOUND)
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
            logger.error(f"Error deleting User {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)
