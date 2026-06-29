import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.specialite.entity.specialite_model import Specialite
from models.specialite.entity.specialite_entity import SpecialiteEntity
from models.specialite.mapper.specialite_mapper import SpecialiteMapper
from models.specialite.repository.specialite_repository import SpecialiteRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class SpecialiteService:
    """Service layer for Specialite business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(SpecialiteEntity, Specialite, SpecialiteMapper)

    async def create(self, domain: Specialite) -> Specialite:
        """Create a new Specialite"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating Specialite: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Specialite]:
        """Get Specialite by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Specialite]:
        """Get all Specialite records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> Specialite:
        """Update Specialite"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete Specialite"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
