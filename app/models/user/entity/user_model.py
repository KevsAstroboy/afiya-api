import re
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from models.sexe.entity.sexe_model import Sexe

from models.statut.entity.statut_model import Statut

from utilities.utilities import Utilities


@dataclass
class User:
    telephone: str
    nom: str
    prenom: str
    type_user: str
    sexe_id: int
    statut_id: int
    id: Optional[int] = None
    email: Optional[str] = None
    annee_naissance: Optional[int] = None
    lieu_naissance: Optional[str] = None
    password: Optional[str] = None
    sexe : Optional[Sexe] = None
    statut : Optional[Statut] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_by: Optional[int] = None
    is_deleted: bool = field(default=False)
    is_defalut_password: bool = field(default=False)
    deletion_reason: Optional[str] = None


    @property
    def is_valid_email(self) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, self.email)) if self.email else False

    @property
    def is_valid_phone_number(self) -> bool:
        if Utilities.is_blank(self.telephone):
            return False

        # Cas numéro avec indicatif +225
        if self.telephone.startswith("+225"):
            # Extraire la partie après +225
            remaining = self.telephone[4:]
            return remaining.isdigit() and len(remaining) == 10

        # Cas numéro sans indicatif
        return self.telephone.isdigit() and len(self.telephone) == 10
