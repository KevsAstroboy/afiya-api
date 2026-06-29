from typing import Optional, List
from models.workflow.entity.step_execution_entity import StepExecutionEntity
from models.workflow.entity.step_execution_model import StepExecution


class StepExecutionMapper:
    @classmethod
    def to_domain(cls, entity: Optional[StepExecutionEntity]) -> Optional[StepExecution]:
        if entity is None:
            return None
        return StepExecution(
            id=entity.id,
            workflow_execution_id=entity.workflow_execution_id,
            step_id=entity.step_id,
            status=entity.status,
            input_data=entity.input_data,
            output_data=entity.output_data,
            llm_response=entity.llm_response,
            error_message=entity.error_message,
            started_at=entity.started_at,
            finished_at=entity.finished_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(domain: StepExecution) -> StepExecutionEntity:
        return StepExecutionEntity(
            id=domain.id,
            workflow_execution_id=domain.workflow_execution_id,
            step_id=domain.step_id,
            status=domain.status,
            input_data=domain.input_data,
            output_data=domain.output_data,
            llm_response=domain.llm_response,
            error_message=domain.error_message,
            started_at=domain.started_at,
            finished_at=domain.finished_at,
        )

    @classmethod
    def to_domain_list(cls, entities: List[StepExecutionEntity]) -> List[StepExecution]:
        return [cls.to_domain(e) for e in entities] if entities else []
