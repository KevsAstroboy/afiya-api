from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class StatutConsultationCreateSchema(BaseModel):
    libelle: str
    code: str

    class Config:
        from_attributes = True


class StatutConsultationUpdateSchema(BaseModel):
    libelle: Optional[str] = None
    code: Optional[str] = None

    class Config:
        from_attributes = True


class StatutConsultationResponseSchema(BaseModel):
    id: int
    libelle: str
    code: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
