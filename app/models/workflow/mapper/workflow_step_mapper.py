from typing import Optional, List
from models.workflow.entity.workflow_step_entity import WorkflowStepEntity
from models.workflow.entity.workflow_step_model import WorkflowStep


class WorkflowStepMapper:
    @classmethod
    def to_domain(cls, entity: Optional[WorkflowStepEntity]) -> Optional[WorkflowStep]:
        if entity is None:
            return None
        return WorkflowStep(
            id=entity.id,
            workflow_id=entity.workflow_id,
            name=entity.name,
            description=entity.description,
            step_order=entity.step_order,
            step_type=entity.step_type,
            llm_prompt=entity.llm_prompt,
            llm_model=entity.llm_model,
            llm_max_tokens=entity.llm_max_tokens,
            on_success_step_id=entity.on_success_step_id,
            on_failure_step_id=entity.on_failure_step_id,
            is_terminal=entity.is_terminal,
            config=entity.config or {},
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
    def to_entity(domain: WorkflowStep) -> WorkflowStepEntity:
        return WorkflowStepEntity(
            id=domain.id,
            workflow_id=domain.workflow_id,
            name=domain.name,
            description=domain.description,
            step_order=domain.step_order,
            step_type=domain.step_type,
            llm_prompt=domain.llm_prompt,
            llm_model=domain.llm_model,
            llm_max_tokens=domain.llm_max_tokens,
            on_success_step_id=domain.on_success_step_id,
            on_failure_step_id=domain.on_failure_step_id,
            is_terminal=domain.is_terminal,
            config=domain.config,
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
    def to_domain_list(cls, entities: List[WorkflowStepEntity]) -> List[WorkflowStep]:
        return [cls.to_domain(e) for e in entities] if entities else []
