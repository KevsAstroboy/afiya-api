from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from core.database import Base

from utilities.common.enums.user_type import UserType


class UserEntity(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telephone = Column(String(20), nullable=True, unique=True)
    nom = Column(String(100), nullable=True)
    prenom = Column(String(100), nullable=True)
    email = Column(String(100), nullable=False, unique=True)
    annee_naissance = Column(Integer, nullable=False)
    lieu_naissance = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    sexe_id = Column(BigInteger, ForeignKey('public.sexe.id'), nullable=True)
    sexe = relationship('SexeEntity', lazy='joined')
    statut_id = Column(BigInteger, ForeignKey('public.statut.id'), nullable=True)
    statut = relationship('StatutEntity', lazy='joined')

    # Audit fields
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    deleted_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    is_default_password = Column(Boolean, nullable=False, default=False)
    deletion_reason = Column(Text, nullable=True)

    def is_patient(self) -> bool:
        return self.type_user == UserType.PATIENT

    def __repr__(self):
        return f"<UserEntity(id={self.id})>"
