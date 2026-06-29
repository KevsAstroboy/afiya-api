import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from models.metric.entity.metric_entity import MetricEntity
from models.metric.entity.metric_model import Metric
from models.metric.mapper.metric_mapper import MetricMapper
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class MetricRepository:
    """Repository for Metric CRUD operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, domain: Metric) -> Metric:
        try:
            entity = MetricMapper.to_entity(domain)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return MetricMapper.to_domain(entity)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating Metric: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Metric]:
        try:
            stmt = select(MetricEntity).where(
                MetricEntity.id == record_id,
                MetricEntity.is_deleted == False
            )
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(
                    f"Metric with id {record_id} not found",
                    ErrorType.NOT_FOUND
                )
            return MetricMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error fetching Metric {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Metric]:
        try:
            stmt = select(MetricEntity).where(MetricEntity.is_deleted == False).offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            return MetricMapper.to_domain_list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error fetching Metric list: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def update(self, record_id: int, updates: dict) -> Metric:
        try:
            await self.get_by_id(record_id)
            stmt = select(MetricEntity).where(MetricEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"Metric {record_id} not found", ErrorType.NOT_FOUND)
            updates["updated_at"] = datetime.now()
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            await self.session.commit()
            await self.session.refresh(entity)
            return MetricMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating Metric {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        try:
            stmt = select(MetricEntity).where(MetricEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"Metric {record_id} not found", ErrorType.NOT_FOUND)
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
            logger.error(f"Error deleting Metric {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)
