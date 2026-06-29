from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ConsultationCreateSchema(BaseModel):
    dossier_medical_id: int
    medecin_id: int
    conversation_id: int
    statut_consultation_id: int
    symptomes_rapportes: Optional[str] = None
    observations_ia: Optional[str] = None
    traitement_prescrit: Optional[str] = None
    recommandations: Optional[str] = None
    notes: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_cloture: Optional[datetime] = None
    notes_internes: Optional[str] = None

    class Config:
        from_attributes = True


class ConsultationUpdateSchema(BaseModel):
    dossier_medical_id: Optional[int] = None
    medecin_id: Optional[int] = None
    conversation_id: Optional[int] = None
    statut_consultation_id: Optional[int] = None
    symptomes_rapportes: Optional[str] = None
    observations_ia: Optional[str] = None
    traitement_prescrit: Optional[str] = None
    recommandations: Optional[str] = None
    notes: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_cloture: Optional[datetime] = None
    notes_internes: Optional[str] = None

    class Config:
        from_attributes = True


class ConsultationResponseSchema(BaseModel):
    id: int
    dossier_medical_id: int
    medecin_id: int
    conversation_id: int
    statut_consultation_id: int
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

    class Config:
        from_attributes = True
