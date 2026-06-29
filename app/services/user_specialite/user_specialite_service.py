import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.user_specialite.entity.user_specialite_model import UserSpecialite
from models.user_specialite.entity.user_specialite_entity import UserSpecialiteEntity
from models.user_specialite.mapper.user_specialite_mapper import UserSpecialiteMapper
from models.user_specialite.repository.user_specialite_repository import UserSpecialiteRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class UserSpecialiteService:
    """Service layer for UserSpecialite business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(UserSpecialiteEntity, UserSpecialite, UserSpecialiteMapper)

    async def create(self, domain: UserSpecialite) -> UserSpecialite:
        """Create a new UserSpecialite"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating UserSpecialite: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[UserSpecialite]:
        """Get UserSpecialite by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserSpecialite]:
        """Get all UserSpecialite records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> UserSpecialite:
        """Update UserSpecialite"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete UserSpecialite"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
