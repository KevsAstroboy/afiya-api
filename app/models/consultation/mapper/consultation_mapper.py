from typing import Optional, List
from models.consultation.entity.consultation_entity import ConsultationEntity
from models.consultation.entity.consultation_model import Consultation


class ConsultationMapper:
    """Mapper for Consultation entity"""

    @classmethod
    def to_domain(cls, entity: Optional[ConsultationEntity]) -> Optional[Consultation]:
        if entity is None:
            return None
        return Consultation(
            id=entity.id,
            dossier_medical_id=entity.dossier_medical_id,
            medecin_id=entity.medecin_id,
            conversation_id=entity.conversation_id,
            statut_consultation_id=entity.statut_consultation_id,
            symptomes_rapportes=entity.symptomes_rapportes,
            observations_ia=entity.observations_ia,
            traitement_prescrit=entity.traitement_prescrit,
            recommandations=entity.recommandations,
            notes=entity.notes,
            date_debut=entity.date_debut,
            date_cloture=entity.date_cloture,
            notes_internes=entity.notes_internes,
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
    def to_entity(domain: Consultation) -> ConsultationEntity:
        return ConsultationEntity(
            id=domain.id,
            dossier_medical_id=domain.dossier_medical_id,
            medecin_id=domain.medecin_id,
            conversation_id=domain.conversation_id,
            statut_consultation_id=domain.statut_consultation_id,
            symptomes_rapportes=domain.symptomes_rapportes,
            observations_ia=domain.observations_ia,
            traitement_prescrit=domain.traitement_prescrit,
            recommandations=domain.recommandations,
            notes=domain.notes,
            date_debut=domain.date_debut,
            date_cloture=domain.date_cloture,
            notes_internes=domain.notes_internes,
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
    def to_domain_list(cls, entities: List[ConsultationEntity]) -> List[Consultation]:
        return [cls.to_domain(e) for e in entities] if entities else []
