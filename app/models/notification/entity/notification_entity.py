from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from core.database import Base


class NotificationEntity(Base):
    __tablename__ = "notification"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('public.user.id'), nullable=True)
    type_notification = Column(String(50), nullable=True)
    titre = Column(String(255), nullable=True)
    contenu = Column(Text, nullable=False)
    lu = Column(Boolean, nullable=True, default=False)
    date_lecture = Column(DateTime, nullable=False)
    notification_metadata = Column("metadata", JSON)

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
        return f"<NotificationEntity(id={self.id})>"
