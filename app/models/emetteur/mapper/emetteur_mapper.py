from typing import Optional, List
from models.emetteur.entity.emetteur_entity import EmetteurEntity
from models.emetteur.entity.emetteur_model import Emetteur


class EmetteurMapper:
    """Mapper for Emetteur entity"""

    @classmethod
    def to_domain(cls, entity: Optional[EmetteurEntity]) -> Optional[Emetteur]:
        if entity is None:
            return None
        return Emetteur(
            id=entity.id,
            type=entity.type,
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
    def to_entity(domain: Emetteur) -> EmetteurEntity:
        return EmetteurEntity(
            id=domain.id,
            type=domain.type,
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
    def to_domain_list(cls, entities: List[EmetteurEntity]) -> List[Emetteur]:
        return [cls.to_domain(e) for e in entities] if entities else []
