from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DossierMedicalCreateSchema(BaseModel):
    user_id: int

    class Config:
        from_attributes = True


class DossierMedicalUpdateSchema(BaseModel):
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class DossierMedicalResponseSchema(BaseModel):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
