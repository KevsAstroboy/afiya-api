from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageCreateSchema(BaseModel):
    conversation_id: int
    emetteur_id: int
    sender_user_id: int
    statut_livraison_id: int
    contenu: str
    type_contenu: str
    date_envoi: datetime
    receiver_user_id: Optional[int] = None
    media_url: Optional[str] = None
    whatsapp_message_id: Optional[str] = None
    date_livraison: Optional[datetime] = None
    date_lecture: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageUpdateSchema(BaseModel):
    conversation_id: Optional[int] = None
    emetteur_id: Optional[int] = None
    sender_user_id: Optional[int] = None
    statut_livraison_id: Optional[int] = None
    contenu: Optional[str] = None
    type_contenu: Optional[str] = None
    date_envoi: Optional[datetime] = None
    receiver_user_id: Optional[int] = None
    media_url: Optional[str] = None
    whatsapp_message_id: Optional[str] = None
    date_livraison: Optional[datetime] = None
    date_lecture: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageResponseSchema(BaseModel):
    id: int
    conversation_id: int
    emetteur_id: int
    sender_user_id: int
    statut_livraison_id: int
    contenu: str
    type_contenu: str
    date_envoi: datetime
    receiver_user_id: Optional[int] = None
    media_url: Optional[str] = None
    whatsapp_message_id: Optional[str] = None
    date_livraison: Optional[datetime] = None
    date_lecture: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
