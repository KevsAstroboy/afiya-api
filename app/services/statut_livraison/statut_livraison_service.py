import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.statut_livraison.entity.statut_livraison_model import StatutLivraison
from models.statut_livraison.entity.statut_livraison_entity import StatutLivraisonEntity
from models.statut_livraison.mapper.statut_livraison_mapper import StatutLivraisonMapper
from models.statut_livraison.repository.statut_livraison_repository import StatutLivraisonRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class StatutLivraisonService:
    """Service layer for StatutLivraison business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(StatutLivraisonEntity, StatutLivraison, StatutLivraisonMapper)

    async def create(self, domain: StatutLivraison) -> StatutLivraison:
        """Create a new StatutLivraison"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating StatutLivraison: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[StatutLivraison]:
        """Get StatutLivraison by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[StatutLivraison]:
        """Get all StatutLivraison records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> StatutLivraison:
        """Update StatutLivraison"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete StatutLivraison"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
