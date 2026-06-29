from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ImagesConsultationCreateSchema(BaseModel):
    consultation_id: int
    url: str
    description: Optional[str] = None
    type_image: Optional[str] = None

    class Config:
        from_attributes = True


class ImagesConsultationUpdateSchema(BaseModel):
    consultation_id: Optional[int] = None
    url: Optional[str] = None
    description: Optional[str] = None
    type_image: Optional[str] = None

    class Config:
        from_attributes = True


class ImagesConsultationResponseSchema(BaseModel):
    id: int
    consultation_id: int
    url: str
    description: Optional[str] = None
    type_image: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
