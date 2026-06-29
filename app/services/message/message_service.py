import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.message.entity.message_model import Message
from models.message.entity.message_entity import MessageEntity
from models.message.mapper.message_mapper import MessageMapper
from models.message.repository.message_repository import MessageRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class MessageService:
    """Service layer for Message business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(MessageEntity, Message, MessageMapper)

    async def create(self, domain: Message) -> Message:
        """Create a new Message"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating Message: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Message]:
        """Get Message by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Message]:
        """Get all Message records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> Message:
        """Update Message"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete Message"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
