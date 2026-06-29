from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSON
from core.database import Base


class DossierMedicalEntity(Base):
    __tablename__ = "dossier_medical"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('public.user.id'), nullable=True, unique=True)

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
        return f"<DossierMedicalEntity(id={self.id})>"
