import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.document.entity.document_model import Document
from models.document.entity.document_entity import DocumentEntity
from models.document.mapper.document_mapper import DocumentMapper
from models.document.repository.document_repository import DocumentRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class DocumentService:
    """Service layer for Document business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(DocumentEntity, Document, DocumentMapper)

    async def create(self, domain: Document) -> Document:
        """Create a new Document"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating Document: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[Document]:
        """Get Document by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get all Document records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> Document:
        """Update Document"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete Document"""
        return await self.repository.delete(record_id, deleted_by=deleted_by)
