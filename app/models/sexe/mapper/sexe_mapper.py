from typing import Optional, List
from models.sexe.entity.sexe_entity import SexeEntity
from models.sexe.entity.sexe_model import Sexe


class SexeMapper:
    """Mapper for Sexe entity"""

    @classmethod
    def to_domain(cls, entity: Optional[SexeEntity]) -> Optional[Sexe]:
        if entity is None:
            return None
        return Sexe(
            id=entity.id,
            libelle=entity.libelle,
            code=entity.code,
            is_deleted=entity.is_deleted,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
            deleted_by=entity.deleted_by,
            deletion_reason=entity.deletion_reason,
        )

    @staticmethod
    def to_entity(domain: Sexe) -> SexeEntity:
        return SexeEntity(
            id=domain.id,
            libelle=domain.libelle,
            code=domain.code,
            is_deleted=domain.is_deleted,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            deleted_at=domain.deleted_at,
            created_by=domain.created_by,
            updated_by=domain.updated_by,
            deleted_by=domain.deleted_by,
            deletion_reason=domain.deletion_reason,
        )

    @classmethod
    def to_domain_list(cls, entities: List[SexeEntity]) -> List[Sexe]:
        return [cls.to_domain(e) for e in entities] if entities else []
