from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class NotificationCreateSchema(BaseModel):
    user_id: int
    type_notification: str
    titre: str
    lu: bool
    contenu: Optional[str] = None
    date_lecture: Optional[datetime] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class NotificationUpdateSchema(BaseModel):
    user_id: Optional[int] = None
    type_notification: Optional[str] = None
    titre: Optional[str] = None
    lu: Optional[bool] = None
    contenu: Optional[str] = None
    date_lecture: Optional[datetime] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class NotificationResponseSchema(BaseModel):
    id: int
    user_id: int
    type_notification: str
    titre: str
    lu: bool
    contenu: Optional[str] = None
    date_lecture: Optional[datetime] = None
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
