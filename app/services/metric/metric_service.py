import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.metric.entity.metric_model import Metric
from models.metric.entity.metric_entity import MetricEntity
from models.metric.mapper.metric_mapper import MetricMapper
from models.metric.repository.metric_repository import MetricRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class MetricService:
    """Service layer for Metric business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(MetricEntity, Metric, MetricMapper)

    async def create(self, domain: Metric) -> Metric:
        """Create a new Metric"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating Metric: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Metric]:
        """Get Metric by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Metric]:
        """Get all Metric records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> Metric:
        """Update Metric"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete Metric"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
