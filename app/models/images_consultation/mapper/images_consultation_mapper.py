from typing import Optional, List
from models.images_consultation.entity.images_consultation_entity import ImagesConsultationEntity
from models.images_consultation.entity.images_consultation_model import ImagesConsultation


class ImagesConsultationMapper:
    """Mapper for ImagesConsultation entity"""

    @classmethod
    def to_domain(cls, entity: Optional[ImagesConsultationEntity]) -> Optional[ImagesConsultation]:
        if entity is None:
            return None
        return ImagesConsultation(
            id=entity.id,
            consultation_id=entity.consultation_id,
            url=entity.url,
            description=entity.description,
            type_image=entity.type_image,
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
    def to_entity(domain: ImagesConsultation) -> ImagesConsultationEntity:
        return ImagesConsultationEntity(
            id=domain.id,
            consultation_id=domain.consultation_id,
            url=domain.url,
            description=domain.description,
            type_image=domain.type_image,
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
    def to_domain_list(cls, entities: List[ImagesConsultationEntity]) -> List[ImagesConsultation]:
        return [cls.to_domain(e) for e in entities] if entities else []
