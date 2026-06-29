from typing import Optional, List
from models.operateur.entity.operateur_entity import OperateurEntity
from models.operateur.entity.operateur_model import Operateur


class OperateurMapper:
    """Mapper for Operateur entity"""

    @classmethod
    def to_domain(cls, entity: Optional[OperateurEntity]) -> Optional[Operateur]:
        if entity is None:
            return None
        return Operateur(
            id=entity.id,
            nom=entity.nom,
            code=entity.code,
            prefixe=entity.prefixe,
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
    def to_entity(domain: Operateur) -> OperateurEntity:
        return OperateurEntity(
            id=domain.id,
            nom=domain.nom,
            code=domain.code,
            prefixe=domain.prefixe,
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
    def to_domain_list(cls, entities: List[OperateurEntity]) -> List[Operateur]:
        return [cls.to_domain(e) for e in entities] if entities else []
