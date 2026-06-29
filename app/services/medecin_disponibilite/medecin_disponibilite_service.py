import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.medecin_disponibilite.entity.medecin_disponibilite_model import MedecinDisponibilite
from models.medecin_disponibilite.entity.medecin_disponibilite_entity import MedecinDisponibiliteEntity
from models.medecin_disponibilite.mapper.medecin_disponibilite_mapper import MedecinDisponibiliteMapper
from models.medecin_disponibilite.repository.medecin_disponibilite_repository import MedecinDisponibiliteRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class MedecinDisponibiliteService:
    """Service layer for MedecinDisponibilite business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(MedecinDisponibiliteEntity, MedecinDisponibilite, MedecinDisponibiliteMapper)

    async def create(self, domain: MedecinDisponibilite) -> MedecinDisponibilite:
        """Create a new MedecinDisponibilite"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating MedecinDisponibilite: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[MedecinDisponibilite]:
        """Get MedecinDisponibilite by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[MedecinDisponibilite]:
        """Get all MedecinDisponibilite records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> MedecinDisponibilite:
        """Update MedecinDisponibilite"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete MedecinDisponibilite"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
