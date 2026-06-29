import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.user_session.entity.user_session_model import UserSession
from models.user_session.entity.user_session_entity import UserSessionEntity
from models.user_session.mapper.user_session_mapper import UserSessionMapper
from models.user_session.repository.user_session_repository import UserSessionRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class UserSessionService:
    """Service layer for UserSession business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(UserSessionEntity, UserSession, UserSessionMapper)

    async def create(self, domain: UserSession) -> UserSession:
        """Create a new UserSession"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating UserSession: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[UserSession]:
        """Get UserSession by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserSession]:
        """Get all UserSession records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> UserSession:
        """Update UserSession"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete UserSession"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
