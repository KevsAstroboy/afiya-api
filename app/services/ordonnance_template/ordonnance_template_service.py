import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.ordonnance_template.entity.ordonnance_template_model import OrdonnanceTemplate
from models.ordonnance_template.entity.ordonnance_template_entity import OrdonnanceTemplateEntity
from models.ordonnance_template.mapper.ordonnance_template_mapper import OrdonnanceTemplateMapper
from models.ordonnance_template.repository.ordonnance_template_repository import OrdonnanceTemplateRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class OrdonnanceTemplateService:
    """Service layer for OrdonnanceTemplate business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(OrdonnanceTemplateEntity, OrdonnanceTemplate, OrdonnanceTemplateMapper)

    async def create(self, domain: OrdonnanceTemplate) -> OrdonnanceTemplate:
        """Create a new OrdonnanceTemplate"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating OrdonnanceTemplate: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[OrdonnanceTemplate]:
        """Get OrdonnanceTemplate by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[OrdonnanceTemplate]:
        """Get all OrdonnanceTemplate records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> OrdonnanceTemplate:
        """Update OrdonnanceTemplate"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete OrdonnanceTemplate"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
