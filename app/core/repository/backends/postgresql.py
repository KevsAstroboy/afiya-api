import logging
from typing import Any, Dict, List, Optional, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from core.repository.interface import RepositoryInterface

logger = logging.getLogger(__name__)
T = TypeVar('T')


class SqlAlchemyRepository(RepositoryInterface[T]):
    """Generic SQLAlchemy repository implementing RepositoryInterface[T].
    Uses entity introspection for table name, columns, and soft-delete auto-detection."""

    def __init__(self, session: AsyncSession, entity_class: type, domain_class: type, mapper: Any):
        self.session = session
        self.entity_class = entity_class
        self.domain_class = domain_class
        self.mapper = mapper
        self._has_soft_delete = hasattr(entity_class, 'is_deleted')

    def _apply_soft_delete_filter(self, stmt):
        if self._has_soft_delete:
            return stmt.where(self.entity_class.is_deleted == False)
        return stmt

    def _build_filters(self, stmt, filters: Dict[str, Any]):
        for key, value in filters.items():
            if hasattr(self.entity_class, key):
                stmt = stmt.where(getattr(self.entity_class, key) == value)
        return stmt

    async def create(self, domain: T) -> T:
        try:
            entity = self.mapper.to_entity(domain)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return self.mapper.to_domain(entity)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating {self.entity_class.__tablename__}: {e}")
            raise

    async def get_by_id(self, record_id: Any) -> Optional[T]:
        stmt = select(self.entity_class).where(self.entity_class.id == record_id)
        stmt = self._apply_soft_delete_filter(stmt)
        result = await self.session.execute(stmt)
        entity = result.scalar_one_or_none()
        return self.mapper.to_domain(entity) if entity else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        stmt = select(self.entity_class).offset(skip).limit(limit)
        stmt = self._apply_soft_delete_filter(stmt)
        result = await self.session.execute(stmt)
        return self.mapper.to_domain_list(result.scalars().all())

    async def update(self, record_id: Any, updates: Dict[str, Any]) -> T:
        try:
            stmt = select(self.entity_class).where(self.entity_class.id == record_id)
            stmt = self._apply_soft_delete_filter(stmt)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise ValueError(f"{self.entity_class.__tablename__} with id {record_id} not found")
            if hasattr(entity, 'updated_at'):
                updates['updated_at'] = datetime.now()
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            await self.session.commit()
            await self.session.refresh(entity)
            return self.mapper.to_domain(entity)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating {self.entity_class.__tablename__} {record_id}: {e}")
            raise

    async def delete(self, record_id: Any, deleted_by: Optional[Any] = None) -> bool:
        try:
            stmt = select(self.entity_class).where(self.entity_class.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise ValueError(f"{self.entity_class.__tablename__} with id {record_id} not found")
            if self._has_soft_delete:
                entity.is_deleted = True
                entity.deleted_at = datetime.now()
                if deleted_by is not None and hasattr(entity, 'deleted_by'):
                    entity.deleted_by = deleted_by
            else:
                await self.session.delete(entity)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting {self.entity_class.__tablename__} {record_id}: {e}")
            raise

    async def find_one(self, filters: Dict[str, Any]) -> Optional[T]:
        stmt = select(self.entity_class)
        stmt = self._apply_soft_delete_filter(stmt)
        stmt = self._build_filters(stmt, filters)
        result = await self.session.execute(stmt)
        entity = result.scalar_one_or_none()
        return self.mapper.to_domain(entity) if entity else None

    async def find_by(self, filters: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[T]:
        stmt = select(self.entity_class).offset(skip).limit(limit)
        stmt = self._apply_soft_delete_filter(stmt)
        stmt = self._build_filters(stmt, filters)
        result = await self.session.execute(stmt)
        return self.mapper.to_domain_list(result.scalars().all())
