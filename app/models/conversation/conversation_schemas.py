from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ConversationCreateSchema(BaseModel):
    user_id: int
    statut_conversation_id: int
    date_debut: datetime
    date_fin: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversationUpdateSchema(BaseModel):
    user_id: Optional[int] = None
    statut_conversation_id: Optional[int] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversationResponseSchema(BaseModel):
    id: int
    user_id: int
    statut_conversation_id: int
    date_debut: datetime
    date_fin: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
