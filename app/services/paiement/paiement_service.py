import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.paiement.entity.paiement_model import Paiement
from models.paiement.entity.paiement_entity import PaiementEntity
from models.paiement.mapper.paiement_mapper import PaiementMapper
from models.paiement.repository.paiement_repository import PaiementRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class PaiementService:
    """Service layer for Paiement business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(PaiementEntity, Paiement, PaiementMapper)

    async def create(self, domain: Paiement) -> Paiement:
        """Create a new Paiement"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating Paiement: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Paiement]:
        """Get Paiement by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Paiement]:
        """Get all Paiement records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> Paiement:
        """Update Paiement"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete Paiement"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
