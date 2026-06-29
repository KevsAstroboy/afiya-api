from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OperateurCreateSchema(BaseModel):
    nom: str
    code: str
    prefixe: Optional[str] = None

    class Config:
        from_attributes = True


class OperateurUpdateSchema(BaseModel):
    nom: Optional[str] = None
    code: Optional[str] = None
    prefixe: Optional[str] = None

    class Config:
        from_attributes = True


class OperateurResponseSchema(BaseModel):
    id: int
    nom: str
    code: str
    prefixe: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
