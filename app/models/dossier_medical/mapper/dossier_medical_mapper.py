from typing import Optional, List
from models.dossier_medical.entity.dossier_medical_entity import DossierMedicalEntity
from models.dossier_medical.entity.dossier_medical_model import DossierMedical


class DossierMedicalMapper:
    """Mapper for DossierMedical entity"""

    @classmethod
    def to_domain(cls, entity: Optional[DossierMedicalEntity]) -> Optional[DossierMedical]:
        if entity is None:
            return None
        return DossierMedical(
            id=entity.id,
            user_id=entity.user_id,
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
    def to_entity(domain: DossierMedical) -> DossierMedicalEntity:
        return DossierMedicalEntity(
            id=domain.id,
            user_id=domain.user_id,
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
    def to_domain_list(cls, entities: List[DossierMedicalEntity]) -> List[DossierMedical]:
        return [cls.to_domain(e) for e in entities] if entities else []
