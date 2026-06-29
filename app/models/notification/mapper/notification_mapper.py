from typing import Optional, List
from models.notification.entity.notification_entity import NotificationEntity
from models.notification.entity.notification_model import Notification


class NotificationMapper:
    """Mapper for Notification entity"""

    @classmethod
    def to_domain(cls, entity: Optional[NotificationEntity]) -> Optional[Notification]:
        if entity is None:
            return None
        return Notification(
            id=entity.id,
            user_id=entity.user_id,
            type_notification=entity.type_notification,
            titre=entity.titre,
            contenu=entity.contenu,
            lu=entity.lu,
            date_lecture=entity.date_lecture,
            metadata=entity.notification_metadata,
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
    def to_entity(domain: Notification) -> NotificationEntity:
        return NotificationEntity(
            id=domain.id,
            user_id=domain.user_id,
            type_notification=domain.type_notification,
            titre=domain.titre,
            contenu=domain.contenu,
            lu=domain.lu,
            date_lecture=domain.date_lecture,
            notification_metadata=domain.metadata,
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
    def to_domain_list(cls, entities: List[NotificationEntity]) -> List[Notification]:
        return [cls.to_domain(e) for e in entities] if entities else []
