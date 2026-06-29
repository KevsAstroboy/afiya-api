import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.emetteur.entity.emetteur_model import Emetteur
from models.emetteur.entity.emetteur_entity import EmetteurEntity
from models.emetteur.mapper.emetteur_mapper import EmetteurMapper
from models.emetteur.repository.emetteur_repository import EmetteurRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class EmetteurService:
    """Service layer for Emetteur business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(EmetteurEntity, Emetteur, EmetteurMapper)

    async def create(self, domain: Emetteur) -> Emetteur:
        """Create a new Emetteur"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating Emetteur: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Emetteur]:
        """Get Emetteur by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Emetteur]:
        """Get all Emetteur records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> Emetteur:
        """Update Emetteur"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete Emetteur"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
