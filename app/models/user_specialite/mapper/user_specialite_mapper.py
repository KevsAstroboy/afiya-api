from typing import Optional, List
from models.user_specialite.entity.user_specialite_entity import UserSpecialiteEntity
from models.user_specialite.entity.user_specialite_model import UserSpecialite


class UserSpecialiteMapper:
    """Mapper for UserSpecialite entity"""

    @classmethod
    def to_domain(cls, entity: Optional[UserSpecialiteEntity]) -> Optional[UserSpecialite]:
        if entity is None:
            return None
        return UserSpecialite(
            id=entity.id,
            user_id=entity.user_id,
            specialite_id=entity.specialite_id,
            is_deleted=entity.is_deleted,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
            deleted_by=entity.deleted_by,
            deletion_reason=entity.deletion_reason,
        )

    @staticmethod
    def to_entity(domain: UserSpecialite) -> UserSpecialiteEntity:
        return UserSpecialiteEntity(
            id=domain.id,
            user_id=domain.user_id,
            specialite_id=domain.specialite_id,
            is_deleted=domain.is_deleted,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            deleted_at=domain.deleted_at,
            created_by=domain.created_by,
            updated_by=domain.updated_by,
            deleted_by=domain.deleted_by,
            deletion_reason=domain.deletion_reason,
        )

    @classmethod
    def to_domain_list(cls, entities: List[UserSpecialiteEntity]) -> List[UserSpecialite]:
        return [cls.to_domain(e) for e in entities] if entities else []
