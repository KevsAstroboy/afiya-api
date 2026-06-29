from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Consultation:
    dossier_medical_id: int
    medecin_id: int
    conversation_id: int
    statut_consultation_id: int
    id: Optional[int] = None
    symptomes_rapportes: Optional[str] = None
    observations_ia: Optional[str] = None
    traitement_prescrit: Optional[str] = None
    recommandations: Optional[str] = None
    notes: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_cloture: Optional[datetime] = None
    notes_internes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    is_deleted: bool = field(default=False)
    deletion_reason: Optional[str] = None
