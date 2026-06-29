from typing import Optional, List
from models.user.entity.user_entity import UserEntity
from models.user.entity.user_model import User

from models.sexe.mapper import SexeMapper

from models.statut.mapper import StatutMapper


class UserMapper:
    """Mapper for User entity"""

    @classmethod
    def to_domain(cls, entity: Optional[UserEntity]) -> Optional[User]:
        if entity is None:
            return None
        return User(
            id=entity.id,
            telephone=entity.telephone,
            nom=entity.nom,
            prenom=entity.prenom,
            email=entity.email,
            annee_naissance=entity.annee_naissance,
            lieu_naissance=entity.lieu_naissance,
            password=entity.password,
            sexe=SexeMapper.to_domain(entity.sexe) if entity.sexe else None,
            statut=StatutMapper.to_domain(entity.statut) if entity.statut else None,
            type_user=entity.type_user,
            sexe_id=entity.sexe_id,
            statut_id=entity.statut_id,
            is_deleted=entity.is_deleted,
            is_defalut_password=entity.is_defalut_password,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
            deleted_by=entity.deleted_by,
            deletion_reason=entity.deletion_reason,
        )

    @staticmethod
    def to_entity(domain: User) -> UserEntity:
        return UserEntity(
            id=domain.id,
            telephone=domain.telephone,
            nom=domain.nom,
            prenom=domain.prenom,
            email=domain.email,
            annee_naissance=domain.annee_naissance,
            lieu_naissance=domain.lieu_naissance,
            password=domain.password,
            type_user=domain.type_user,
            sexe_id=domain.sexe_id,
            statut_id=domain.statut_id,
            is_deleted=domain.is_deleted,
            is_defalut_password=domain.is_defalut_password,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            deleted_at=domain.deleted_at,
            created_by=domain.created_by,
            updated_by=domain.updated_by,
            deleted_by=domain.deleted_by,
            deletion_reason=domain.deletion_reason,
        )

    @classmethod
    def to_domain_list(cls, entities: List[UserEntity]) -> List[User]:
        return [cls.to_domain(e) for e in entities] if entities else []
