import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from models.statut_livraison.entity.statut_livraison_entity import StatutLivraisonEntity
from models.statut_livraison.entity.statut_livraison_model import StatutLivraison
from models.statut_livraison.mapper.statut_livraison_mapper import StatutLivraisonMapper
from core.exceptions.exceptions import BusinessException, ErrorType

logger = logging.getLogger(__name__)


class StatutLivraisonRepository:
    """Repository for StatutLivraison CRUD operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, domain: StatutLivraison) -> StatutLivraison:
        try:
            entity = StatutLivraisonMapper.to_entity(domain)
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return StatutLivraisonMapper.to_domain(entity)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating StatutLivraison: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[StatutLivraison]:
        try:
            stmt = select(StatutLivraisonEntity).where(
                StatutLivraisonEntity.id == record_id,
                StatutLivraisonEntity.is_deleted == False
            )
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(
                    f"StatutLivraison with id {record_id} not found",
                    ErrorType.NOT_FOUND
                )
            return StatutLivraisonMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error fetching StatutLivraison {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[StatutLivraison]:
        try:
            stmt = select(StatutLivraisonEntity).where(StatutLivraisonEntity.is_deleted == False).offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            return StatutLivraisonMapper.to_domain_list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error fetching StatutLivraison list: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def update(self, record_id: int, updates: dict) -> StatutLivraison:
        try:
            await self.get_by_id(record_id)
            stmt = select(StatutLivraisonEntity).where(StatutLivraisonEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"StatutLivraison {record_id} not found", ErrorType.NOT_FOUND)
            updates["updated_at"] = datetime.now()
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            await self.session.commit()
            await self.session.refresh(entity)
            return StatutLivraisonMapper.to_domain(entity)
        except BusinessException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating StatutLivraison {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        try:
            stmt = select(StatutLivraisonEntity).where(StatutLivraisonEntity.id == record_id)
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()
            if not entity:
                raise BusinessException(f"StatutLivraison {record_id} not found", ErrorType.NOT_FOUND)
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
            logger.error(f"Error deleting StatutLivraison {record_id}: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)
