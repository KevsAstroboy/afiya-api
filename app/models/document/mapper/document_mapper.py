from typing import Optional, List
from models.document.entity.document_entity import DocumentEntity
from models.document.entity.document_model import Document


class DocumentMapper:
    """Mapper for Document entity"""

    @classmethod
    def to_domain(cls, entity: Optional[DocumentEntity]) -> Optional[Document]:
        if entity is None:
            return None
        return Document(
            id=entity.id,
            entity_type=entity.entity_type,
            entity_id=entity.entity_id,
            type_document=entity.type_document,
            nom_fichier=entity.nom_fichier,
            url=entity.url,
            mime_type=entity.mime_type,
            taille_bytes=entity.taille_bytes,
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
    def to_entity(domain: Document) -> DocumentEntity:
        return DocumentEntity(
            id=domain.id,
            entity_type=domain.entity_type,
            entity_id=domain.entity_id,
            type_document=domain.type_document,
            nom_fichier=domain.nom_fichier,
            url=domain.url,
            mime_type=domain.mime_type,
            taille_bytes=domain.taille_bytes,
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
    def to_domain_list(cls, entities: List[DocumentEntity]) -> List[Document]:
        return [cls.to_domain(e) for e in entities] if entities else []
