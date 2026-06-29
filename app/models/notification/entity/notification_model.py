from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Notification:
    user_id: int
    type_notification: str
    titre: str
    lu: bool
    id: Optional[int] = None
    contenu: Optional[str] = None
    date_lecture: Optional[datetime] = None
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    is_deleted: bool = field(default=False)
    deletion_reason: Optional[str] = None
