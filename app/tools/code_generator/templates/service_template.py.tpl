import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.{table_name}.entity.{table_name}_model import {ClassName}
from app.models.{table_name}.repository.{table_name}_repository import {ClassName}Repository
from app.core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class {ClassName}Service:
    """Service layer for {ClassName} business logic"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = {ClassName}Repository(session)

    async def create(self, domain: {ClassName}) -> {ClassName}:
        """Create a new {ClassName}"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating {ClassName}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[{ClassName}]:
        """Get {ClassName} by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[{ClassName}]:
        """Get all {ClassName} records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> {ClassName}:
        """Update {ClassName}"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete {ClassName}"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
