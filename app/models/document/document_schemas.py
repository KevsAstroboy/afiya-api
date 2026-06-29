from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentCreateSchema(BaseModel):
    entity_type: str
    entity_id: int
    type_document: str
    nom_fichier: str
    url: str
    mime_type: Optional[str] = None
    taille_bytes: Optional[int] = None

    class Config:
        from_attributes = True


class DocumentUpdateSchema(BaseModel):
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    type_document: Optional[str] = None
    nom_fichier: Optional[str] = None
    url: Optional[str] = None
    mime_type: Optional[str] = None
    taille_bytes: Optional[int] = None

    class Config:
        from_attributes = True


class DocumentResponseSchema(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    type_document: str
    nom_fichier: str
    url: str
    mime_type: Optional[str] = None
    taille_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
