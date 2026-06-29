import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.operateur.entity.operateur_model import Operateur
from models.operateur.entity.operateur_entity import OperateurEntity
from models.operateur.mapper.operateur_mapper import OperateurMapper
from models.operateur.repository.operateur_repository import OperateurRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class OperateurService:
    """Service layer for Operateur business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(OperateurEntity, Operateur, OperateurMapper)

    async def create(self, domain: Operateur) -> Operateur:
        """Create a new Operateur"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating Operateur: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Operateur]:
        """Get Operateur by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Operateur]:
        """Get all Operateur records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> Operateur:
        """Update Operateur"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete Operateur"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
