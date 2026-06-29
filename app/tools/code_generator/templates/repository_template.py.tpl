import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.{table_name}.entity.{table_name}_entity import {ClassName}Entity
from app.models.{table_name}.entity.{table_name}_model import {ClassName}
from app.models.{table_name}.mapper.{table_name}_mapper import {ClassName}Mapper
from app.core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class {ClassName}Repository:
    """Repository for {ClassName} CRUD operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, domain: {ClassName}) -> {ClassName}:
        try:
            entity = {ClassName}Mapper.to_entity(domain)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return {ClassName}Mapper.to_domain(entity)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating {ClassName}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[{ClassName}]:
        try:
            stmt = select({ClassName}Entity).where(
                {ClassName}Entity.id == record_id,
                {ClassName}Entity.is_deleted == False
            )
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(
                    f"{ClassName} with id {record_id} not found",
                    ErrorType.NOT_FOUND
                )
            return {ClassName}Mapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error fetching {ClassName} {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[{ClassName}]:
        try:
            stmt = select({ClassName}Entity).where(
                {ClassName}Entity.is_deleted == False
            ).offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            return {ClassName}Mapper.to_domain_list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error fetching {ClassName} list: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def update(self, record_id: int, updates: dict) -> {ClassName}:
        try:
            await self.get_by_id(record_id)
            stmt = select({ClassName}Entity).where({ClassName}Entity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"{ClassName} {record_id} not found", ErrorType.NOT_FOUND)
            updates["updated_at"] = datetime.now()
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            await self.session.commit()
            await self.session.refresh(entity)
            return {ClassName}Mapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating {ClassName} {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        try:
            stmt = select({ClassName}Entity).where({ClassName}Entity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"{ClassName} {record_id} not found", ErrorType.NOT_FOUND)
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
            logger.error(f"Error deleting {ClassName} {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)
