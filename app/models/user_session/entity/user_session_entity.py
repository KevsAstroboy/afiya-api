from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from core.database import Base


class UserSessionEntity(Base):
    __tablename__ = "user_session"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('public.user.id'), nullable=True)
    token = Column(String(255), nullable=True, unique=True)
    refresh_token = Column(String(255), nullable=False)
    device_info = Column(JSON, nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    revoked = Column(Boolean, nullable=True, default=False)
    revoked_at = Column(DateTime, nullable=False)

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
        return f"<UserSessionEntity(id={self.id})>"
