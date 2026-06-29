import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.avis_consultation.entity.avis_consultation_model import AvisConsultation
from models.avis_consultation.entity.avis_consultation_entity import AvisConsultationEntity
from models.avis_consultation.mapper.avis_consultation_mapper import AvisConsultationMapper
from models.avis_consultation.repository.avis_consultation_repository import AvisConsultationRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class AvisConsultationService:
    """Service layer for AvisConsultation business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(AvisConsultationEntity, AvisConsultation, AvisConsultationMapper)

    async def create(self, domain: AvisConsultation) -> AvisConsultation:
        """Create a new AvisConsultation"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating AvisConsultation: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[AvisConsultation]:
        """Get AvisConsultation by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[AvisConsultation]:
        """Get all AvisConsultation records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> AvisConsultation:
        """Update AvisConsultation"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete AvisConsultation"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
