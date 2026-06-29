from typing import Optional, List
from models.paiement.entity.paiement_entity import PaiementEntity
from models.paiement.entity.paiement_model import Paiement


class PaiementMapper:
    """Mapper for Paiement entity"""

    @classmethod
    def to_domain(cls, entity: Optional[PaiementEntity]) -> Optional[Paiement]:
        if entity is None:
            return None
        return Paiement(
            id=entity.id,
            consultation_id=entity.consultation_id,
            statut_paiement_id=entity.statut_paiement_id,
            operateur_id=entity.operateur_id,
            montant=entity.montant,
            devise=entity.devise,
            fournisseur=entity.fournisseur,
            transaction_id=entity.transaction_id,
            reference_externe=entity.reference_externe,
            transaction_date=entity.transaction_date,
            request_payload=entity.request_payload,
            response_payload=entity.response_payload,
            verify_payload=entity.verify_payload,
            metadata=entity.metadata,
            date_validation=entity.date_validation,
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
    def to_entity(domain: Paiement) -> PaiementEntity:
        return PaiementEntity(
            id=domain.id,
            consultation_id=domain.consultation_id,
            statut_paiement_id=domain.statut_paiement_id,
            operateur_id=domain.operateur_id,
            montant=domain.montant,
            devise=domain.devise,
            fournisseur=domain.fournisseur,
            transaction_id=domain.transaction_id,
            reference_externe=domain.reference_externe,
            transaction_date=domain.transaction_date,
            request_payload=domain.request_payload,
            response_payload=domain.response_payload,
            verify_payload=domain.verify_payload,
            paiement_metadata=domain.metadata,
            date_validation=domain.date_validation,
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
    def to_domain_list(cls, entities: List[PaiementEntity]) -> List[Paiement]:
        return [cls.to_domain(e) for e in entities] if entities else []
