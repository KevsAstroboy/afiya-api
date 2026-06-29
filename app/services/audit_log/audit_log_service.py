import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.audit_log.entity.audit_log_model import AuditLog
from models.audit_log.entity.audit_log_entity import AuditLogEntity
from models.audit_log.mapper.audit_log_mapper import AuditLogMapper
from models.audit_log.repository.audit_log_repository import AuditLogRepository
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class AuditLogService:
    """Service layer for AuditLog business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.repository = backend.get_repository(AuditLogEntity, AuditLog, AuditLogMapper)

    async def create(self, domain: AuditLog) -> AuditLog:
        """Create a new AuditLog"""
        try:
            return await self.repository.create(domain)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating AuditLog: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[AuditLog]:
        """Get AuditLog by ID"""
        return await self.repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get all AuditLog records"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> AuditLog:
        """Update AuditLog"""
        return await self.repository.update(record_id, updates)

    async def delete(self, record_id: int) -> bool:
        """Delete AuditLog"""
        return await self.repository.delete(record_id)
