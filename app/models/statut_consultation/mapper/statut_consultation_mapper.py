from typing import Optional, List
from models.statut_consultation.entity.statut_consultation_entity import StatutConsultationEntity
from models.statut_consultation.entity.statut_consultation_model import StatutConsultation


class StatutConsultationMapper:
    """Mapper for StatutConsultation entity"""

    @classmethod
    def to_domain(cls, entity: Optional[StatutConsultationEntity]) -> Optional[StatutConsultation]:
        if entity is None:
            return None
        return StatutConsultation(
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
    def to_entity(domain: StatutConsultation) -> StatutConsultationEntity:
        return StatutConsultationEntity(
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
    def to_domain_list(cls, entities: List[StatutConsultationEntity]) -> List[StatutConsultation]:
        return [cls.to_domain(e) for e in entities] if entities else []
