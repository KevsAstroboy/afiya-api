import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.conversation.entity.conversation_model import Conversation
from models.conversation.entity.conversation_entity import ConversationEntity
from models.conversation.mapper.conversation_mapper import ConversationMapper
from models.conversation.repository.conversation_repository import ConversationRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class ConversationService:
    """Service layer for Conversation business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(ConversationEntity, Conversation, ConversationMapper)

    async def create(self, domain: Conversation) -> Conversation:
        """Create a new Conversation"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating Conversation: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Conversation]:
        """Get Conversation by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Conversation]:
        """Get all Conversation records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> Conversation:
        """Update Conversation"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete Conversation"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
