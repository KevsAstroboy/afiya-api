import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from models.statut_paiement.entity.statut_paiement_entity import StatutPaiementEntity
from models.statut_paiement.entity.statut_paiement_model import StatutPaiement
from models.statut_paiement.mapper.statut_paiement_mapper import StatutPaiementMapper
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class StatutPaiementRepository:
    """Repository for StatutPaiement CRUD operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, domain: StatutPaiement) -> StatutPaiement:
        try:
            entity = StatutPaiementMapper.to_entity(domain)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return StatutPaiementMapper.to_domain(entity)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating StatutPaiement: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[StatutPaiement]:
        try:
            stmt = select(StatutPaiementEntity).where(
                StatutPaiementEntity.id == record_id,
                StatutPaiementEntity.is_deleted == False
            )
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(
                    f"StatutPaiement with id {record_id} not found",
                    ErrorType.NOT_FOUND
                )
            return StatutPaiementMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error fetching StatutPaiement {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[StatutPaiement]:
        try:
            stmt = select(StatutPaiementEntity).where(StatutPaiementEntity.is_deleted == False).offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            return StatutPaiementMapper.to_domain_list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error fetching StatutPaiement list: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def update(self, record_id: int, updates: dict) -> StatutPaiement:
        try:
            await self.get_by_id(record_id)
            stmt = select(StatutPaiementEntity).where(StatutPaiementEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"StatutPaiement {record_id} not found", ErrorType.NOT_FOUND)
            updates["updated_at"] = datetime.now()
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            await self.session.commit()
            await self.session.refresh(entity)
            return StatutPaiementMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating StatutPaiement {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        try:
            stmt = select(StatutPaiementEntity).where(StatutPaiementEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"StatutPaiement {record_id} not found", ErrorType.NOT_FOUND)
            # Soft delete
            entity.is_deleted = True
            entity.deleted_at = datetime.now()
            entity.deleted_by = deleted_by
            await self.session.commit()
            return True
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting StatutPaiement {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)
