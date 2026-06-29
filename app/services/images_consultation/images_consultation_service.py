import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.images_consultation.entity.images_consultation_model import ImagesConsultation
from models.images_consultation.entity.images_consultation_entity import ImagesConsultationEntity
from models.images_consultation.mapper.images_consultation_mapper import ImagesConsultationMapper
from models.images_consultation.repository.images_consultation_repository import ImagesConsultationRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class ImagesConsultationService:
    """Service layer for ImagesConsultation business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(ImagesConsultationEntity, ImagesConsultation, ImagesConsultationMapper)

    async def create(self, domain: ImagesConsultation) -> ImagesConsultation:
        """Create a new ImagesConsultation"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating ImagesConsultation: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[ImagesConsultation]:
        """Get ImagesConsultation by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ImagesConsultation]:
        """Get all ImagesConsultation records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> ImagesConsultation:
        """Update ImagesConsultation"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete ImagesConsultation"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
