from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class OrdonnanceTemplate:
    nom: str
    contenu: str
    est_public: bool
    id: Optional[int] = None
    medecin_id: Optional[int] = None
    specialite_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    is_deleted: bool = field(default=False)
    deletion_reason: Optional[str] = None
