from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EmetteurCreateSchema(BaseModel):
    type: str
    code: str

    class Config:
        from_attributes = True


class EmetteurUpdateSchema(BaseModel):
    type: Optional[str] = None
    code: Optional[str] = None

    class Config:
        from_attributes = True


class EmetteurResponseSchema(BaseModel):
    id: int
    type: str
    code: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
