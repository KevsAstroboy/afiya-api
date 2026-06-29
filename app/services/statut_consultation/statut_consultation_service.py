import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.statut_consultation.entity.statut_consultation_model import StatutConsultation
from models.statut_consultation.entity.statut_consultation_entity import StatutConsultationEntity
from models.statut_consultation.mapper.statut_consultation_mapper import StatutConsultationMapper
from models.statut_consultation.repository.statut_consultation_repository import StatutConsultationRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class StatutConsultationService:
    """Service layer for StatutConsultation business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(StatutConsultationEntity, StatutConsultation, StatutConsultationMapper)

    async def create(self, domain: StatutConsultation) -> StatutConsultation:
        """Create a new StatutConsultation"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating StatutConsultation: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[StatutConsultation]:
        """Get StatutConsultation by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[StatutConsultation]:
        """Get all StatutConsultation records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> StatutConsultation:
        """Update StatutConsultation"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete StatutConsultation"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
