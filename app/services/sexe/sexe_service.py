import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.sexe.entity.sexe_model import Sexe
from models.sexe.entity.sexe_entity import SexeEntity
from models.sexe.mapper.sexe_mapper import SexeMapper
from models.sexe.repository.sexe_repository import SexeRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class SexeService:
    """Service layer for Sexe business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(SexeEntity, Sexe, SexeMapper)

    async def create(self, domain: Sexe) -> Sexe:
        """Create a new Sexe"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating Sexe: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Sexe]:
        """Get Sexe by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Sexe]:
        """Get all Sexe records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> Sexe:
        """Update Sexe"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete Sexe"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
