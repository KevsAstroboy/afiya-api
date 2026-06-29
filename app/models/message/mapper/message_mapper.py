from typing import Optional, List
from models.message.entity.message_entity import MessageEntity
from models.message.entity.message_model import Message


class MessageMapper:
    """Mapper for Message entity"""

    @classmethod
    def to_domain(cls, entity: Optional[MessageEntity]) -> Optional[Message]:
        if entity is None:
            return None
        return Message(
            id=entity.id,
            conversation_id=entity.conversation_id,
            emetteur_id=entity.emetteur_id,
            sender_user_id=entity.sender_user_id,
            receiver_user_id=entity.receiver_user_id,
            statut_livraison_id=entity.statut_livraison_id,
            contenu=entity.contenu,
            type_contenu=entity.type_contenu,
            media_url=entity.media_url,
            whatsapp_message_id=entity.whatsapp_message_id,
            date_envoi=entity.date_envoi,
            date_livraison=entity.date_livraison,
            date_lecture=entity.date_lecture,
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
    def to_entity(domain: Message) -> MessageEntity:
        return MessageEntity(
            id=domain.id,
            conversation_id=domain.conversation_id,
            emetteur_id=domain.emetteur_id,
            sender_user_id=domain.sender_user_id,
            receiver_user_id=domain.receiver_user_id,
            statut_livraison_id=domain.statut_livraison_id,
            contenu=domain.contenu,
            type_contenu=domain.type_contenu,
            media_url=domain.media_url,
            whatsapp_message_id=domain.whatsapp_message_id,
            date_envoi=domain.date_envoi,
            date_livraison=domain.date_livraison,
            date_lecture=domain.date_lecture,
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
    def to_domain_list(cls, entities: List[MessageEntity]) -> List[Message]:
        return [cls.to_domain(e) for e in entities] if entities else []
