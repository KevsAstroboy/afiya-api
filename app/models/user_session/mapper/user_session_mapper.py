from typing import Optional, List
from models.user_session.entity.user_session_entity import UserSessionEntity
from models.user_session.entity.user_session_model import UserSession


class UserSessionMapper:
    """Mapper for UserSession entity"""

    @classmethod
    def to_domain(cls, entity: Optional[UserSessionEntity]) -> Optional[UserSession]:
        if entity is None:
            return None
        return UserSession(
            id=entity.id,
            user_id=entity.user_id,
            token=entity.token,
            refresh_token=entity.refresh_token,
            device_info=entity.device_info,
            ip_address=entity.ip_address,
            user_agent=entity.user_agent,
            expires_at=entity.expires_at,
            revoked=entity.revoked,
            revoked_at=entity.revoked_at,
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
    def to_entity(domain: UserSession) -> UserSessionEntity:
        return UserSessionEntity(
            id=domain.id,
            user_id=domain.user_id,
            token=domain.token,
            refresh_token=domain.refresh_token,
            device_info=domain.device_info,
            ip_address=domain.ip_address,
            user_agent=domain.user_agent,
            expires_at=domain.expires_at,
            revoked=domain.revoked,
            revoked_at=domain.revoked_at,
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
    def to_domain_list(cls, entities: List[UserSessionEntity]) -> List[UserSession]:
        return [cls.to_domain(e) for e in entities] if entities else []
