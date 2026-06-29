from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PaiementCreateSchema(BaseModel):
    consultation_id: int
    statut_paiement_id: int
    montant: float
    devise: str
    fournisseur: str
    operateur_id: Optional[int] = None
    transaction_id: Optional[str] = None
    reference_externe: Optional[str] = None
    transaction_date: Optional[datetime] = None
    request_payload: Optional[str] = None
    response_payload: Optional[str] = None
    verify_payload: Optional[str] = None
    metadata: Optional[dict] = None
    date_validation: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaiementUpdateSchema(BaseModel):
    consultation_id: Optional[int] = None
    statut_paiement_id: Optional[int] = None
    montant: Optional[float] = None
    devise: Optional[str] = None
    fournisseur: Optional[str] = None
    operateur_id: Optional[int] = None
    transaction_id: Optional[str] = None
    reference_externe: Optional[str] = None
    transaction_date: Optional[datetime] = None
    request_payload: Optional[str] = None
    response_payload: Optional[str] = None
    verify_payload: Optional[str] = None
    metadata: Optional[dict] = None
    date_validation: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaiementResponseSchema(BaseModel):
    id: int
    consultation_id: int
    statut_paiement_id: int
    montant: float
    devise: str
    fournisseur: str
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

    class Config:
        from_attributes = True
