from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AvisConsultationCreateSchema(BaseModel):
    consultation_id: int
    note: int
    commentaire: Optional[str] = None

    class Config:
        from_attributes = True


class AvisConsultationUpdateSchema(BaseModel):
    consultation_id: Optional[int] = None
    note: Optional[int] = None
    commentaire: Optional[str] = None

    class Config:
        from_attributes = True


class AvisConsultationResponseSchema(BaseModel):
    id: int
    consultation_id: int
    note: int
    commentaire: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
