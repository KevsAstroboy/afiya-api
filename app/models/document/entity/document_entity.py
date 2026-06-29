from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from core.database import Base


class DocumentEntity(Base):
    __tablename__ = "document"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(BigInteger, nullable=True)
    type_document = Column(String(50), nullable=True)
    nom_fichier = Column(String(255), nullable=True)
    url = Column(Text, nullable=True)
    mime_type = Column(String(100), nullable=False)
    taille_bytes = Column(BigInteger, nullable=False)

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
        return f"<DocumentEntity(id={self.id})>"
