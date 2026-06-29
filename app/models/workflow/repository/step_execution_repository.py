import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from models.workflow.entity.step_execution_entity import StepExecutionEntity
from models.workflow.entity.step_execution_model import StepExecution
from models.workflow.mapper.step_execution_mapper import StepExecutionMapper
from core.repository.backends.postgresql import SqlAlchemyRepository
from core.workflow.types import StepResult

logger = logging.getLogger(__name__)


class StepExecutionRepository(SqlAlchemyRepository[StepExecution]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, StepExecutionEntity, StepExecution, StepExecutionMapper)

    async def save_step_execution(self, workflow_execution_id: str, result: StepResult):
        entity = StepExecutionEntity(
            workflow_execution_id=int(workflow_execution_id.replace("-", ""), 16) % (2**63),
            step_id=int(result.step_id) if result.step_id.isdigit() else 0,
            status=result.status.value,
            output_data={"output": result.output} if result.output is not None else None,
            error_message=result.error,
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
        )
        self.session.add(entity)
        await self.session.commit()
