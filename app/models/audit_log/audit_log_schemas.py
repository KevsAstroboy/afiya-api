from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AuditLogCreateSchema(BaseModel):
    table_name: str
    record_id: int
    action: str
    user_id: Optional[int] = None
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


class AuditLogUpdateSchema(BaseModel):
    table_name: Optional[str] = None
    record_id: Optional[int] = None
    action: Optional[str] = None
    user_id: Optional[int] = None
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


class AuditLogResponseSchema(BaseModel):
    id: int
    table_name: str
    record_id: int
    action: str
    user_id: Optional[int] = None
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
