from typing import Optional, List
from models.conversation.entity.conversation_entity import ConversationEntity
from models.conversation.entity.conversation_model import Conversation


class ConversationMapper:
    """Mapper for Conversation entity"""

    @classmethod
    def to_domain(cls, entity: Optional[ConversationEntity]) -> Optional[Conversation]:
        if entity is None:
            return None
        return Conversation(
            id=entity.id,
            user_id=entity.user_id,
            statut_conversation_id=entity.statut_conversation_id,
            date_debut=entity.date_debut,
            date_fin=entity.date_fin,
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
    def to_entity(domain: Conversation) -> ConversationEntity:
        return ConversationEntity(
            id=domain.id,
            user_id=domain.user_id,
            statut_conversation_id=domain.statut_conversation_id,
            date_debut=domain.date_debut,
            date_fin=domain.date_fin,
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
    def to_domain_list(cls, entities: List[ConversationEntity]) -> List[Conversation]:
        return [cls.to_domain(e) for e in entities] if entities else []
