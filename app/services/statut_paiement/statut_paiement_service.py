import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.statut_paiement.entity.statut_paiement_model import StatutPaiement
from models.statut_paiement.entity.statut_paiement_entity import StatutPaiementEntity
from models.statut_paiement.mapper.statut_paiement_mapper import StatutPaiementMapper
from models.statut_paiement.repository.statut_paiement_repository import StatutPaiementRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class StatutPaiementService:
    """Service layer for StatutPaiement business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(StatutPaiementEntity, StatutPaiement, StatutPaiementMapper)

    async def create(self, domain: StatutPaiement) -> StatutPaiement:
        """Create a new StatutPaiement"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating StatutPaiement: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[StatutPaiement]:
        """Get StatutPaiement by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[StatutPaiement]:
        """Get all StatutPaiement records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> StatutPaiement:
        """Update StatutPaiement"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete StatutPaiement"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
