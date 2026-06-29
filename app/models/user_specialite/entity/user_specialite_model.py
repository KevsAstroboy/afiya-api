from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class UserSpecialite:
    user_id: int
    specialite_id: int
    id: Optional[int] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    is_deleted: bool = field(default=False)
    deletion_reason: Optional[str] = None
