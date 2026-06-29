from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSON
from core.database import Base


class ConsultationEntity(Base):
    __tablename__ = "consultation"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    dossier_medical_id = Column(BigInteger, ForeignKey('public.dossier_medical.id'), nullable=True)
    medecin_id = Column(BigInteger, ForeignKey('public.user.id'), nullable=True)
    conversation_id = Column(BigInteger, ForeignKey('public.conversation.id'), nullable=True, unique=True)
    statut_consultation_id = Column(BigInteger, ForeignKey('public.statut_consultation.id'), nullable=True)
    symptomes_rapportes = Column(Text, nullable=False)
    observations_ia = Column(Text, nullable=False)
    traitement_prescrit = Column(Text, nullable=False)
    recommandations = Column(Text, nullable=False)
    notes = Column(Text, nullable=False)
    date_debut = Column(DateTime, nullable=False)
    date_cloture = Column(DateTime, nullable=False)
    notes_internes = Column(Text, nullable=False)

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
        return f"<ConsultationEntity(id={self.id})>"
