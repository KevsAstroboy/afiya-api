from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, JSON, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from core.database import Base


class PaiementEntity(Base):
    __tablename__ = "paiement"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    consultation_id = Column(BigInteger, ForeignKey('public.consultation.id'), nullable=True)
    statut_paiement_id = Column(BigInteger, ForeignKey('public.statut_paiement.id'), nullable=True)
    operateur_id = Column(BigInteger, ForeignKey('public.operateur.id'), nullable=False)
    montant = Column(Numeric(10, 2), nullable=True)
    devise = Column(String(3), nullable=True)
    fournisseur = Column(String(50), nullable=True)
    transaction_id = Column(String(255), nullable=False)
    reference_externe = Column(String(100), nullable=False, unique=True)
    transaction_date = Column(DateTime, nullable=False)
    request_payload = Column(Text, nullable=False)
    response_payload = Column(Text, nullable=False)
    verify_payload = Column(Text, nullable=False)
    paiement_metadata = Column(JSON, nullable=False)
    date_validation = Column(DateTime, nullable=False)

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
        return f"<PaiementEntity(id={self.id})>"
