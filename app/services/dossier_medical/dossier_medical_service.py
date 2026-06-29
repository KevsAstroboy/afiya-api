import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.dossier_medical.entity.dossier_medical_model import DossierMedical
from models.dossier_medical.entity.dossier_medical_entity import DossierMedicalEntity
from models.dossier_medical.mapper.dossier_medical_mapper import DossierMedicalMapper
from models.dossier_medical.repository.dossier_medical_repository import DossierMedicalRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class DossierMedicalService:
    """Service layer for DossierMedical business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(DossierMedicalEntity, DossierMedical, DossierMedicalMapper)

    async def create(self, domain: DossierMedical) -> DossierMedical:
        """Create a new DossierMedical"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating DossierMedical: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[DossierMedical]:
        """Get DossierMedical by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[DossierMedical]:
        """Get all DossierMedical records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> DossierMedical:
        """Update DossierMedical"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete DossierMedical"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
