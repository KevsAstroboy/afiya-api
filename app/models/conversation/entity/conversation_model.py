from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Conversation:
    user_id: int
    statut_conversation_id: int
    date_debut: datetime
    id: Optional[int] = None
    date_fin: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    is_deleted: bool = field(default=False)
    deletion_reason: Optional[str] = None
