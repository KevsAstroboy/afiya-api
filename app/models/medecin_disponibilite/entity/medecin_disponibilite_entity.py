from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, Text, Time, func
from sqlalchemy.dialects.postgresql import JSON
from core.database import Base


class MedecinDisponibiliteEntity(Base):
    __tablename__ = "medecin_disponibilite"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    medecin_id = Column(BigInteger, ForeignKey('public.user.id'), nullable=True)
    jour_semaine = Column(Integer, nullable=True)
    heure_debut = Column(Time, nullable=True)
    heure_fin = Column(Time, nullable=True)
    actif = Column(Boolean, nullable=True, default=True)

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
        return f"<MedecinDisponibiliteEntity(id={self.id})>"
