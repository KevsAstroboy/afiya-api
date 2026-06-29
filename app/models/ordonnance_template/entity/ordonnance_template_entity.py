from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from core.database import Base


class OrdonnanceTemplateEntity(Base):
    __tablename__ = "ordonnance_template"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    medecin_id = Column(BigInteger, ForeignKey('public.user.id'), nullable=False)
    specialite_id = Column(BigInteger, ForeignKey('public.specialite.id'), nullable=False)
    nom = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    contenu = Column(Text, nullable=True)
    est_public = Column(Boolean, nullable=True, default=False)

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
        return f"<OrdonnanceTemplateEntity(id={self.id})>"
