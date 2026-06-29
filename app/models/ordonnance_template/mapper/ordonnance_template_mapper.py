from typing import Optional, List
from models.ordonnance_template.entity.ordonnance_template_entity import OrdonnanceTemplateEntity
from models.ordonnance_template.entity.ordonnance_template_model import OrdonnanceTemplate


class OrdonnanceTemplateMapper:
    """Mapper for OrdonnanceTemplate entity"""

    @classmethod
    def to_domain(cls, entity: Optional[OrdonnanceTemplateEntity]) -> Optional[OrdonnanceTemplate]:
        if entity is None:
            return None
        return OrdonnanceTemplate(
            id=entity.id,
            medecin_id=entity.medecin_id,
            specialite_id=entity.specialite_id,
            nom=entity.nom,
            description=entity.description,
            contenu=entity.contenu,
            est_public=entity.est_public,
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
    def to_entity(domain: OrdonnanceTemplate) -> OrdonnanceTemplateEntity:
        return OrdonnanceTemplateEntity(
            id=domain.id,
            medecin_id=domain.medecin_id,
            specialite_id=domain.specialite_id,
            nom=domain.nom,
            description=domain.description,
            contenu=domain.contenu,
            est_public=domain.est_public,
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
    def to_domain_list(cls, entities: List[OrdonnanceTemplateEntity]) -> List[OrdonnanceTemplate]:
        return [cls.to_domain(e) for e in entities] if entities else []
