from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from core.database import Base


class MetricEntity(Base):
    __tablename__ = "metric"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    consultation_id = Column(BigInteger, ForeignKey('public.consultation.id'), nullable=True)
    type_metric = Column(String(50), nullable=True)
    valeur = Column(Numeric(10, 2), nullable=True)
    unite = Column(String(20), nullable=True)
    date_mesure = Column(DateTime, nullable=True, server_default=func.now())

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
        return f"<MetricEntity(id={self.id})>"
