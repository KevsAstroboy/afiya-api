from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserSessionCreateSchema(BaseModel):
    user_id: int
    token: str
    expires_at: datetime
    revoked: bool
    refresh_token: Optional[str] = None
    device_info: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserSessionUpdateSchema(BaseModel):
    user_id: Optional[int] = None
    token: Optional[str] = None
    expires_at: Optional[datetime] = None
    revoked: Optional[bool] = None
    refresh_token: Optional[str] = None
    device_info: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserSessionResponseSchema(BaseModel):
    id: int
    user_id: int
    token: str
    expires_at: datetime
    revoked: bool
    refresh_token: Optional[str] = None
    device_info: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    revoked_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
