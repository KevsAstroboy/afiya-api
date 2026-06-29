from typing import Optional, List
from models.workflow.entity.workflow_entity import WorkflowEntity
from models.workflow.entity.workflow_model import Workflow


class WorkflowMapper:
    @classmethod
    def to_domain(cls, entity: Optional[WorkflowEntity]) -> Optional[Workflow]:
        if entity is None:
            return None
        return Workflow(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
            deleted_by=entity.deleted_by,
            is_deleted=entity.is_deleted,
            deletion_reason=entity.deletion_reason,
        )

    @staticmethod
    def to_entity(domain: Workflow) -> WorkflowEntity:
        return WorkflowEntity(
            id=domain.id,
            name=domain.name,
            description=domain.description,
            is_active=domain.is_active,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            deleted_at=domain.deleted_at,
            created_by=domain.created_by,
            updated_by=domain.updated_by,
            deleted_by=domain.deleted_by,
            is_deleted=domain.is_deleted,
            deletion_reason=domain.deletion_reason,
        )

    @classmethod
    def to_domain_list(cls, entities: List[WorkflowEntity]) -> List[Workflow]:
        return [cls.to_domain(e) for e in entities] if entities else []
