from typing import Optional, List
from models.avis_consultation.entity.avis_consultation_entity import AvisConsultationEntity
from models.avis_consultation.entity.avis_consultation_model import AvisConsultation


class AvisConsultationMapper:
    """Mapper for AvisConsultation entity"""

    @classmethod
    def to_domain(cls, entity: Optional[AvisConsultationEntity]) -> Optional[AvisConsultation]:
        if entity is None:
            return None
        return AvisConsultation(
            id=entity.id,
            consultation_id=entity.consultation_id,
            note=entity.note,
            commentaire=entity.commentaire,
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
    def to_entity(domain: AvisConsultation) -> AvisConsultationEntity:
        return AvisConsultationEntity(
            id=domain.id,
            consultation_id=domain.consultation_id,
            note=domain.note,
            commentaire=domain.commentaire,
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
    def to_domain_list(cls, entities: List[AvisConsultationEntity]) -> List[AvisConsultation]:
        return [cls.to_domain(e) for e in entities] if entities else []
