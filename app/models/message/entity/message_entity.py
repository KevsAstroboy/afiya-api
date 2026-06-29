from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from core.database import Base


class MessageEntity(Base):
    __tablename__ = "message"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id = Column(BigInteger, ForeignKey('public.conversation.id'), nullable=True)
    emetteur_id = Column(BigInteger, ForeignKey('public.emetteur.id'), nullable=True)
    sender_user_id = Column(BigInteger, ForeignKey('public.user.id'), nullable=True)
    receiver_user_id = Column(BigInteger, ForeignKey('public.user.id'), nullable=False)
    statut_livraison_id = Column(BigInteger, ForeignKey('public.statut_livraison.id'), nullable=True)
    contenu = Column(Text, nullable=True)
    type_contenu = Column(String(20), nullable=True)
    media_url = Column(Text, nullable=False)
    whatsapp_message_id = Column(String(100), nullable=False, unique=True)
    date_envoi = Column(DateTime, nullable=True, server_default=func.now())
    date_livraison = Column(DateTime, nullable=False)
    date_lecture = Column(DateTime, nullable=False)

    # Audit fields
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    deleted_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deletion_reason = Column(Text, nullable=True)

    def __repr__(self):
        return f"<MessageEntity(id={self.id})>"
