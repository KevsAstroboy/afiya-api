from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Paiement:
    consultation_id: int
    statut_paiement_id: int
    montant: float
    devise: str
    fournisseur: str
    id: Optional[int] = None
    operateur_id: Optional[int] = None
    transaction_id: Optional[str] = None
    reference_externe: Optional[str] = None
    transaction_date: Optional[datetime] = None
    request_payload: Optional[str] = None
    response_payload: Optional[str] = None
    verify_payload: Optional[str] = None
    metadata: Optional[dict] = None
    date_validation: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    is_deleted: bool = field(default=False)
    deletion_reason: Optional[str] = None
