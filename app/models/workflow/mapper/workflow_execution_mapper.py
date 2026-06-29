from typing import Optional, List
from models.workflow.entity.workflow_execution_entity import WorkflowExecutionEntity
from models.workflow.entity.workflow_execution_model import WorkflowExecution


class WorkflowExecutionMapper:
    @classmethod
    def to_domain(cls, entity: Optional[WorkflowExecutionEntity]) -> Optional[WorkflowExecution]:
        if entity is None:
            return None
        return WorkflowExecution(
            id=entity.id,
            workflow_id=entity.workflow_id,
            status=entity.status,
            input_data=entity.input_data,
            output_data=entity.output_data,
            started_at=entity.started_at,
            finished_at=entity.finished_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(domain: WorkflowExecution) -> WorkflowExecutionEntity:
        return WorkflowExecutionEntity(
            id=domain.id,
            workflow_id=domain.workflow_id,
            status=domain.status,
            input_data=domain.input_data,
            output_data=domain.output_data,
            started_at=domain.started_at,
            finished_at=domain.finished_at,
        )

    @classmethod
    def to_domain_list(cls, entities: List[WorkflowExecutionEntity]) -> List[WorkflowExecution]:
        return [cls.to_domain(e) for e in entities] if entities else []
