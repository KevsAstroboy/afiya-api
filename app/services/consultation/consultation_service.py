import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.consultation.entity.consultation_model import Consultation
from models.consultation.entity.consultation_entity import ConsultationEntity
from models.consultation.mapper.consultation_mapper import ConsultationMapper
from models.consultation.repository.consultation_repository import ConsultationRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class ConsultationService:
    """Service layer for Consultation business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(ConsultationEntity, Consultation, ConsultationMapper)

    async def create(self, domain: Consultation) -> Consultation:
        """Create a new Consultation"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating Consultation: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Consultation]:
        """Get Consultation by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Consultation]:
        """Get all Consultation records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> Consultation:
        """Update Consultation"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete Consultation"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
