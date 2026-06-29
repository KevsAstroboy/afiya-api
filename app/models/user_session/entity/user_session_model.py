from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class UserSession:
    user_id: int
    token: str
    expires_at: datetime
    revoked: bool
    id: Optional[int] = None
    refresh_token: Optional[str] = None
    device_info: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    revoked_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    is_deleted: bool = field(default=False)
    deletion_reason: Optional[str] = None
