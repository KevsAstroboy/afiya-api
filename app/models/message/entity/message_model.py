from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Message:
    conversation_id: int
    emetteur_id: int
    sender_user_id: int
    statut_livraison_id: int
    contenu: str
    type_contenu: str
    date_envoi: datetime
    id: Optional[int] = None
    receiver_user_id: Optional[int] = None
    media_url: Optional[str] = None
    whatsapp_message_id: Optional[str] = None
    date_livraison: Optional[datetime] = None
    date_lecture: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    is_deleted: bool = field(default=False)
    deletion_reason: Optional[str] = None
