from sqlalchemy import BigInteger, Column, DateTime, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from core.database import Base


class AuditLogEntity(Base):
    __tablename__ = "audit_log"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    table_name = Column(String(100), nullable=True)
    record_id = Column(BigInteger, nullable=True)
    action = Column(String(20), nullable=True)
    user_id = Column(BigInteger, nullable=False)
    old_values = Column(JSON, nullable=False)
    new_values = Column(JSON, nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=False)


    def __repr__(self):
        return f"<AuditLogEntity(id={self.id})>"
