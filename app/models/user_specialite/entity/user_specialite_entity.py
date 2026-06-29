from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSON
from core.database import Base


class UserSpecialiteEntity(Base):
    __tablename__ = "user_specialite"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('public.user.id'), nullable=True, unique=True)
    specialite_id = Column(BigInteger, ForeignKey('public.specialite.id'), nullable=True, unique=True)

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
        return f"<UserSpecialiteEntity(id={self.id})>"
