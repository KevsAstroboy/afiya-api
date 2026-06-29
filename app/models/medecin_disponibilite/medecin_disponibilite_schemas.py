from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MedecinDisponibiliteCreateSchema(BaseModel):
    medecin_id: int
    jour_semaine: int
    heure_debut: str
    heure_fin: str
    actif: bool

    class Config:
        from_attributes = True


class MedecinDisponibiliteUpdateSchema(BaseModel):
    medecin_id: Optional[int] = None
    jour_semaine: Optional[int] = None
    heure_debut: Optional[str] = None
    heure_fin: Optional[str] = None
    actif: Optional[bool] = None

    class Config:
        from_attributes = True


class MedecinDisponibiliteResponseSchema(BaseModel):
    id: int
    medecin_id: int
    jour_semaine: int
    heure_debut: str
    heure_fin: str
    actif: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
