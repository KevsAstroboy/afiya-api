from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OrdonnanceTemplateCreateSchema(BaseModel):
    nom: str
    contenu: str
    est_public: bool
    medecin_id: Optional[int] = None
    specialite_id: Optional[int] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class OrdonnanceTemplateUpdateSchema(BaseModel):
    nom: Optional[str] = None
    contenu: Optional[str] = None
    est_public: Optional[bool] = None
    medecin_id: Optional[int] = None
    specialite_id: Optional[int] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class OrdonnanceTemplateResponseSchema(BaseModel):
    id: int
    nom: str
    contenu: str
    est_public: bool
    medecin_id: Optional[int] = None
    specialite_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
