from typing import Optional, List
from models.specialite.entity.specialite_entity import SpecialiteEntity
from models.specialite.entity.specialite_model import Specialite


class SpecialiteMapper:
    """Mapper for Specialite entity"""

    @classmethod
    def to_domain(cls, entity: Optional[SpecialiteEntity]) -> Optional[Specialite]:
        if entity is None:
            return None
        return Specialite(
            id=entity.id,
            nom=entity.nom,
            code=entity.code,
            description=entity.description,
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
    def to_entity(domain: Specialite) -> SpecialiteEntity:
        return SpecialiteEntity(
            id=domain.id,
            nom=domain.nom,
            code=domain.code,
            description=domain.description,
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
    def to_domain_list(cls, entities: List[SpecialiteEntity]) -> List[Specialite]:
        return [cls.to_domain(e) for e in entities] if entities else []
