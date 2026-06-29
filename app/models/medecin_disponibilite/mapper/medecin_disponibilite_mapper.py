from typing import Optional, List
from models.medecin_disponibilite.entity.medecin_disponibilite_entity import MedecinDisponibiliteEntity
from models.medecin_disponibilite.entity.medecin_disponibilite_model import MedecinDisponibilite


class MedecinDisponibiliteMapper:
    """Mapper for MedecinDisponibilite entity"""

    @classmethod
    def to_domain(cls, entity: Optional[MedecinDisponibiliteEntity]) -> Optional[MedecinDisponibilite]:
        if entity is None:
            return None
        return MedecinDisponibilite(
            id=entity.id,
            medecin_id=entity.medecin_id,
            jour_semaine=entity.jour_semaine,
            heure_debut=entity.heure_debut,
            heure_fin=entity.heure_fin,
            actif=entity.actif,
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
    def to_entity(domain: MedecinDisponibilite) -> MedecinDisponibiliteEntity:
        return MedecinDisponibiliteEntity(
            id=domain.id,
            medecin_id=domain.medecin_id,
            jour_semaine=domain.jour_semaine,
            heure_debut=domain.heure_debut,
            heure_fin=domain.heure_fin,
            actif=domain.actif,
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
    def to_domain_list(cls, entities: List[MedecinDisponibiliteEntity]) -> List[MedecinDisponibilite]:
        return [cls.to_domain(e) for e in entities] if entities else []
