from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SpecialiteCreateSchema(BaseModel):
    nom: str
    code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SpecialiteUpdateSchema(BaseModel):
    nom: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SpecialiteResponseSchema(BaseModel):
    id: int
    nom: str
    code: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
