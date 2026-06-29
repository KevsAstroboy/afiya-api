import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from models.audit_log.entity.audit_log_entity import AuditLogEntity
from models.audit_log.entity.audit_log_model import AuditLog
from models.audit_log.mapper.audit_log_mapper import AuditLogMapper
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class AuditLogRepository:
    """Repository for AuditLog CRUD operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, domain: AuditLog) -> AuditLog:
        try:
            entity = AuditLogMapper.to_entity(domain)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return AuditLogMapper.to_domain(entity)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating AuditLog: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[AuditLog]:
        try:
            stmt = select(AuditLogEntity).where(
                AuditLogEntity.id == record_id
            )
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(
                    f"AuditLog with id {record_id} not found",
                    ErrorType.NOT_FOUND
                )
            return AuditLogMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error fetching AuditLog {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        try:
            stmt = select(AuditLogEntity).offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            return AuditLogMapper.to_domain_list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error fetching AuditLog list: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def update(self, record_id: int, updates: dict) -> AuditLog:
        try:
            await self.get_by_id(record_id)
            stmt = select(AuditLogEntity).where(AuditLogEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"AuditLog {record_id} not found", ErrorType.NOT_FOUND)
            updates["updated_at"] = datetime.now()
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            await self.session.commit()
            await self.session.refresh(entity)
            return AuditLogMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating AuditLog {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        try:
            stmt = select(AuditLogEntity).where(AuditLogEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"AuditLog {record_id} not found", ErrorType.NOT_FOUND)
            # Hard delete
            await self.session.delete(entity)
            await self.session.commit()
            return True
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting AuditLog {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)
