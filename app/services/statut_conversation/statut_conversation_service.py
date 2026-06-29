import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.statut_conversation.entity.statut_conversation_model import StatutConversation
from models.statut_conversation.entity.statut_conversation_entity import StatutConversationEntity
from models.statut_conversation.mapper.statut_conversation_mapper import StatutConversationMapper
from models.statut_conversation.repository.statut_conversation_repository import StatutConversationRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class StatutConversationService:
    """Service layer for StatutConversation business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(StatutConversationEntity, StatutConversation, StatutConversationMapper)

    async def create(self, domain: StatutConversation) -> StatutConversation:
        """Create a new StatutConversation"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating StatutConversation: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[StatutConversation]:
        """Get StatutConversation by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[StatutConversation]:
        """Get all StatutConversation records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> StatutConversation:
        """Update StatutConversation"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete StatutConversation"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
