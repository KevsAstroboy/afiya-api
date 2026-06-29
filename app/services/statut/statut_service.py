import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.statut.entity.statut_model import Statut
from models.statut.entity.statut_entity import StatutEntity
from models.statut.mapper.statut_mapper import StatutMapper
from models.statut.repository.statut_repository import StatutRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class StatutService:
    """Service layer for Statut business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(StatutEntity, Statut, StatutMapper)

    async def create(self, domain: Statut) -> Statut:
        """Create a new Statut"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating Statut: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Statut]:
        """Get Statut by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Statut]:
        """Get all Statut records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> Statut:
        """Update Statut"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete Statut"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
