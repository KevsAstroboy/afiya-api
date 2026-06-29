from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Document:
    entity_type: str
    entity_id: int
    type_document: str
    nom_fichier: str
    url: str
    id: Optional[int] = None
    mime_type: Optional[str] = None
    taille_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    is_deleted: bool = field(default=False)
    deletion_reason: Optional[str] = None
