from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


from models.user.entity.user_model import User


class UserCreateSchema(BaseModel):
    telephone: Optional[str]= None
    nom: Optional[str]= None
    prenom: Optional[str]= None
    type_user: Optional[str]= None
    sexe_id: Optional[int]= None
    statut_id: Optional[int]= None
    email: Optional[str] = None
    annee_naissance: Optional[int] = None
    lieu_naissance: Optional[str] = None
    password: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    telephone: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    type_user: Optional[str] = None
    sexe_id: Optional[int] = None
    statut_id: Optional[int] = None
    email: Optional[str] = None
    annee_naissance: Optional[int] = None
    lieu_naissance: Optional[str] = None
    password: Optional[str] = None

    class Config:
        from_attributes = True





class UserResponseSchema(BaseModel):
    id: int
    telephone: str
    nom: str
    prenom: str
    type_user: str
    sexe_id: Optional[int] = None
    statut_id: Optional[int] = None
    sexe_libelle: Optional[str] = None
    statut_libelle: Optional[str] = None
    email: Optional[str] = None
    annee_naissance: Optional[int] = None
    lieu_naissance: Optional[str] = None

    @staticmethod
    def to_response(domain: "User") -> "UserResponseSchema":
        return UserResponseSchema(
            id=domain.id,
            telephone=domain.telephone,
            nom=domain.nom,
            prenom=domain.prenom,
            type_user=domain.type_user,
            sexe_id=domain.sexe_id,
            statut_id=domain.statut_id,
            sexe_libelle=domain.sexe.libelle if domain.sexe else None,
            statut_libelle=domain.statut.libelle if domain.statut else None,
            email=domain.email,
            annee_naissance=domain.annee_naissance,
            lieu_naissance=domain.lieu_naissance,
        )

    class Config:
        from_attributes = True
