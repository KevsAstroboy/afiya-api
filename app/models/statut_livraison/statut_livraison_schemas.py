from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class StatutLivraisonCreateSchema(BaseModel):
    libelle: str
    code: str

    class Config:
        from_attributes = True


class StatutLivraisonUpdateSchema(BaseModel):
    libelle: Optional[str] = None
    code: Optional[str] = None

    class Config:
        from_attributes = True


class StatutLivraisonResponseSchema(BaseModel):
    id: int
    libelle: str
    code: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
